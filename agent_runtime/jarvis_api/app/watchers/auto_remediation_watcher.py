import asyncio
import logging
from app.database import SessionLocal
from app.services.deco_supervisor import DecoSupervisor

logger = logging.getLogger(__name__)

async def start_auto_remediation_watcher():
    """
    Periodically runs the DecoSupervisor auto-remediation cycle.
    Runs every 5 minutes.
    """
    logger.info("Starting Auto-Remediation Watcher...")
    while True:
        try:
            db = SessionLocal()
            try:
                await DecoSupervisor.run_auto_remediation_cycle(db)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in Auto-Remediation Watcher: {e}")
        
        await asyncio.sleep(300) # 5 minutes
