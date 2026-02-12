import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect

# Get DB URL from env or default (matching orchestrator_api default)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://jarvis_user:change_me_securely@postgres:5432/jarvis_core")

async def migrate():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.connect() as conn:
        # Check if table exists and has column
        # Since inspection is async-hostile in some versions, we try to select the column
        try:
            print("Checking for asset_id in cases table...")
            await conn.execute(text("SELECT asset_id FROM cases LIMIT 1"))
            print("Column asset_id ALREADY EXISTS.")
        except Exception as e:
            print(f"Column check failed (likely missing): {e}")
            await conn.rollback()
            print("Attempting to ADD column asset_id...")
            try:
                await conn.execute(text("ALTER TABLE cases ADD COLUMN asset_id VARCHAR"))
                await conn.commit()
                print("SUCCESS: Added asset_id column.")
            except Exception as e2:
                print(f"FAILED to add column: {e2}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
