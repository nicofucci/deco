from sqlalchemy import text
from app.db.session import SessionLocal

def patch_db():
    db = SessionLocal()
    try:
        print("Adding agent_id column to reports table...")
        db.execute(text("ALTER TABLE reports ADD COLUMN agent_id VARCHAR"))
        db.commit()
        print("Done.")
    except Exception as e:
        print(f"Error (maybe already exists?): {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    patch_db()
