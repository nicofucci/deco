from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded for migration reliability
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://deco:deco123@postgres:5432/decocore")

def run_migration():
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    ctx = conn.execution_options(isolation_level="AUTOCOMMIT")

    try:
        # 1. Create predictive_signals table
        logger.info("Creating predictive_signals table...")
        ctx.execute(text("""
            CREATE TABLE IF NOT EXISTS predictive_signals (
                id VARCHAR PRIMARY KEY,
                client_id VARCHAR NOT NULL REFERENCES clients(id),
                asset_id VARCHAR REFERENCES network_assets(id),
                signal_type VARCHAR NOT NULL,
                severity VARCHAR NOT NULL, -- low, medium, high, critical
                description TEXT,
                score_delta INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
            );
        """))
        logger.info("Table predictive_signals created/verified.")

        # 2. Add predictive_risk_score to clients
        logger.info("Checking predictive_risk_score column in clients...")
        result = ctx.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='clients' AND column_name='predictive_risk_score';
        """))
        
        if not result.fetchone():
            logger.info("Adding predictive_risk_score column to clients...")
            ctx.execute(text("""
                ALTER TABLE clients 
                ADD COLUMN predictive_risk_score INTEGER DEFAULT 100;
            """))
            logger.info("Column added.")
        else:
            logger.info("Column predictive_risk_score already exists.")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
