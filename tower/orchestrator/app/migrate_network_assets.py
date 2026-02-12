from app.db.session import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            print("Migrating network_assets table...")
            conn.execute(text("ALTER TABLE network_assets ADD COLUMN IF NOT EXISTS origin_type VARCHAR DEFAULT 'unknown'"))
            conn.execute(text("ALTER TABLE network_assets ADD COLUMN IF NOT EXISTS confidence_score INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE network_assets ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]'"))
            conn.commit()
            print("Migration successful")
        except Exception as e:
            print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
