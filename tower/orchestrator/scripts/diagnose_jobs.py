import logging
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Hardcode URL as verified in previous steps to avoid config issues in scripts
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://deco:deco123@postgres:5432/decocore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JobDiagnosis")

def check_stuck_jobs():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        logger.info("--- 1. Checking Database for STUCK JOBS ---")
        
        query = text("""
            SELECT id, type, status, agent_id, created_at, started_at
            FROM scan_jobs
            WHERE status = 'running'
            AND created_at < NOW() - INTERVAL '5 minutes'
            ORDER BY created_at DESC
        """)
        
        result = conn.execute(query)
        jobs = result.fetchall()
        
        if not jobs:
            logger.info("No stuck running jobs found (older than 5 mins).")
        else:
            logger.info(f"Found {len(jobs)} stuck jobs.")
            for job in jobs:
                logger.info(f"JOBID: {job.id} | Type: {job.type} | Agent: {job.agent_id} | Created: {job.created_at} | Started: {job.started_at}")

        # Check total 'running' count regardless of time
        logger.info("--- Concurrency Check ---")
        count_query = text("SELECT count(*) FROM scan_jobs WHERE status = 'running'")
        total_running = conn.execute(count_query).scalar()
        logger.info(f"Total jobs currently in RUNNING state: {total_running}")

if __name__ == "__main__":
    check_stuck_jobs()
