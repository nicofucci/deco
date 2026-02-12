from sqlalchemy import text
from app.db.session import engine

def update_schema():
    print("Checking for commission_percent in partners table...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='partners' AND column_name='commission_percent'"))
        if not result.fetchone():
            print("Adding commission_percent column to partners table...")
            conn.execute(text("ALTER TABLE partners ADD COLUMN commission_percent INTEGER NOT NULL DEFAULT 50"))
            conn.commit()
            print("Column added.")
        else:
            print("Column commission_percent already exists.")

if __name__ == "__main__":
    update_schema()
