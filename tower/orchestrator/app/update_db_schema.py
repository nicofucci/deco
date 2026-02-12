from sqlalchemy import text
from app.db.session import engine
from app.models.domain import Base

def update_schema():
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("New tables created (if they didn't exist).")

    print("Checking for partner_id in clients table...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clients' AND column_name='partner_id'"))
        if not result.fetchone():
            print("Adding partner_id column to clients table...")
            conn.execute(text("ALTER TABLE clients ADD COLUMN partner_id VARCHAR NULL REFERENCES partners(id)"))
            conn.commit()
            print("Column added.")
        else:
            print("Column partner_id already exists.")

    print("Checking for local_ip in agents table...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='agents' AND column_name='local_ip'"))
        if not result.fetchone():
            print("Adding network columns to agents table...")
            conn.execute(text("ALTER TABLE agents ADD COLUMN local_ip VARCHAR NULL"))
            conn.execute(text("ALTER TABLE agents ADD COLUMN primary_cidr VARCHAR NULL"))
            conn.execute(text("ALTER TABLE agents ADD COLUMN interfaces JSON NULL"))
            conn.commit()
            print("Columns added.")
        else:
            print("Network columns already exist.")

if __name__ == "__main__":
    update_schema()
