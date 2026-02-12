from app.db.session import engine
from sqlalchemy import text

def migrate_db():
    print("Migrating DB...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN region VARCHAR DEFAULT 'us-east-1'"))
            print("Added region to clients.")
        except Exception as e:
            print(f"Error adding region to clients (maybe exists): {e}")
            
        try:
            conn.execute(text("ALTER TABLE agents ADD COLUMN region VARCHAR DEFAULT 'us-east-1'"))
            print("Added region to agents.")
        except Exception as e:
            print(f"Error adding region to agents (maybe exists): {e}")
        
        conn.commit()
    print("Migration done.")

if __name__ == "__main__":
    migrate_db()
