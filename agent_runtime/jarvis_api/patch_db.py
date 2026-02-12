from app.database import engine
from sqlalchemy import text

def patch_db():
    print("Patching database...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE messages ADD COLUMN metadata JSONB DEFAULT '{}'"))
            conn.commit()
            print("✅ Column 'metadata' added successfully.")
        except Exception as e:
            print(f"❌ Error (might already exist): {e}")

if __name__ == "__main__":
    patch_db()
