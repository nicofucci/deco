from app.db.session import engine
from app.models.domain import Base
from sqlalchemy import text

def migrate():
    print("Applying X-RAY V2 Migrations...")
    conn = engine.connect()
    
    # 1. Add columns to network_assets
    try:
        conn.execute(text("ALTER TABLE network_assets ADD COLUMN status VARCHAR DEFAULT 'new'"))
        conn.execute(text("ALTER TABLE network_assets ADD COLUMN times_seen INTEGER DEFAULT 1"))
        print("[+] Added columns status, times_seen to network_assets")
    except Exception as e:
        print(f"[-] Columns might already exist: {e}")

    # 2. Create History Table
    # Base.metadata.create_all handles creation if not exists
    Base.metadata.create_all(bind=engine)
    print("[+] Created missing tables (NetworkAssetHistory)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
