import sys
import os
import secrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent dir to path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/app")

from app.models.domain import Partner
from app.db.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jarvis_user:change_me_securely@localhost:5432/jarvis_core")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_keys():
    db = SessionLocal()
    try:
        partners = db.query(Partner).filter(Partner.partner_api_key == None).all()
        print(f"Found {len(partners)} partners without API Key.")
        
        for p in partners:
            new_key = secrets.token_hex(16)
            p.partner_api_key = new_key
            print(f"Generated key for {p.email}: {new_key}")
            
        db.commit()
        print("Migration completed.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_keys()
