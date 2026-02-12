import logging
import os
import sys

# Ensure app is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal, engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB_Migration")

def migrate():
    db = SessionLocal()
    try:
        logger.info("Starting migration for network_asset_history table...")
        
        # Add 'reason' column if not exists
        try:
            db.execute(text("ALTER TABLE network_asset_history ADD COLUMN reason VARCHAR"))
            logger.info("Added 'reason' column.")
        except Exception as e:
            logger.info(f"Column 'reason' might already exist or error: {e}")
            db.rollback()

        # Add 'changed_at' column if not exists
        try:
            db.execute(text("ALTER TABLE network_asset_history ADD COLUMN changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()"))
            logger.info("Added 'changed_at' column.")
        except Exception as e:
            logger.info(f"Column 'changed_at' might already exist or error: {e}")
            db.rollback()

        db.commit()
        logger.info("Migration completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
