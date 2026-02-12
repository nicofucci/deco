import logging
import os
import sys
from sqlalchemy import create_engine, text

# Hardcode URL for reliability in script
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://deco:deco123@postgres:5432/decocore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutofixMigration")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.begin()
        try:
            logger.info("Creating autofix_playbooks table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS autofix_playbooks (
                    id VARCHAR PRIMARY KEY,
                    client_id VARCHAR REFERENCES clients(id),
                    asset_id VARCHAR REFERENCES network_assets(id),
                    vulnerability_id VARCHAR REFERENCES network_vulnerabilities(id),
                    title VARCHAR NOT NULL,
                    playbook_json JSONB NOT NULL,
                    risk_level VARCHAR DEFAULT 'medium',
                    status VARCHAR DEFAULT 'draft',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    CONSTRAINT fk_client FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE,
                    CONSTRAINT fk_asset FOREIGN KEY(asset_id) REFERENCES network_assets(id) ON DELETE CASCADE
                );
            """))

            logger.info("Creating autofix_executions table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS autofix_executions (
                    id VARCHAR PRIMARY KEY,
                    playbook_id VARCHAR REFERENCES autofix_playbooks(id) ON DELETE CASCADE,
                    agent_id VARCHAR REFERENCES agents(id) ON DELETE SET NULL,
                    execution_mode VARCHAR DEFAULT 'manual',
                    status VARCHAR DEFAULT 'pending',
                    logs TEXT,
                    started_at TIMESTAMPTZ,
                    finished_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """))
            
            conn.commit()
            logger.info("Migration successful.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Migration failed: {e}")
            raise e

if __name__ == "__main__":
    migrate()
