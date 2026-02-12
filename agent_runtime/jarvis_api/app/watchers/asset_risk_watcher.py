import asyncio
import logging
from app.database import SessionLocal
from app.risk.risk_service import RiskService
from app.models.alerts import SystemAlert

logger = logging.getLogger(__name__)

async def start_asset_risk_watcher():
    """
    Recalculates Asset Risk every 10 minutes.
    """
    logger.info("Starting Asset Risk Watcher...")
    while True:
        try:
            db = SessionLocal()
            try:
                assets = db.query(SystemAlert.asset_id).distinct().filter(SystemAlert.asset_id != None).all()
                asset_ids = [a[0] for a in assets]
                
                service = RiskService(db)
                for asset_id in asset_ids:
                    service.calculate_and_save_risk('asset', asset_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in Asset Risk Watcher: {e}")
        
        await asyncio.sleep(600)
