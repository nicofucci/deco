
import sys
import os
import logging
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.models.domain import Base, AgentVersion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB_Updater")

def create_table():
    logger.info("Ensuring agent_versions table exists...")
    Base.metadata.create_all(bind=engine)
    logger.info("Table creation check complete.")

if __name__ == "__main__":
    create_table()
