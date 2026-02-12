import sys
import os
import secrets
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append("/opt/deco/tower/orchestrator")

from app.models.domain import Client
from app.db.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://deco:deco123@deco-sec-postgres:5432/deco_orchestrator")

def migrate():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    print("Starting migration...")

    # 1. Add columns if not exist
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE clients ADD COLUMN IF NOT EXISTS agent_api_key VARCHAR"))
            conn.execute(text("ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_panel_api_key VARCHAR"))
            conn.execute(text("ALTER TABLE clients ALTER COLUMN api_key DROP NOT NULL"))
            conn.commit()
        print("Columns added.")
    except Exception as e:
        print(f"Error adding columns: {e}")

    # 2. Migrate data
    clients = db.query(Client).all()
    for client in clients:
        print(f"Migrating client: {client.name} ({client.id})")
        
        # If already migrated, skip or update? Let's check if empty
        if not client.client_panel_api_key:
            client.client_panel_api_key = client.api_key
        
        if not client.agent_api_key:
            if client.name == "Thinkpad Nico":
                client.agent_api_key = "agk_" + secrets.token_hex(16)
                client.client_panel_api_key = "ck_" + secrets.token_hex(16)
                print(f"  -> Generated specific keys for Thinkpad Nico")
            else:
                client.agent_api_key = secrets.token_hex(16)
                print(f"  -> Generated new agent key")

    db.commit()
    print("Migration complete.")
    db.close()

if __name__ == "__main__":
    migrate()
