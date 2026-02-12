import asyncio
import logging
from app.database import SessionLocal
from app.risk.risk_service import RiskService

logger = logging.getLogger(__name__)

async def start_risk_global_watcher():
    """
    Recalculates Global Risk every 5 minutes.
    """
    logger.info("Starting Global Risk Watcher...")
    while True:
        try:
            db = SessionLocal()
            try:
                service = RiskService(db)
                service.calculate_and_save_risk('global', 'global')
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in Global Risk Watcher: {e}")
        
        await asyncio.sleep(300)
