import asyncio
import logging
from app.database import SessionLocal
from app.risk.risk_service import RiskService
# We need a way to get all clients. 
# Assuming we can query alerts to find active clients or have a client service.
# For simplicity, we will extract unique client_ids from alerts table or a mock list.
from app.models.alerts import SystemAlert

logger = logging.getLogger(__name__)

async def start_client_risk_watcher():
    """
    Recalculates Client Risk every 10 minutes.
    """
    logger.info("Starting Client Risk Watcher...")
    while True:
        try:
            db = SessionLocal()
            try:
                # Find all clients referenced in alerts (active or not)
                # In a real system, we'd query the Client table.
                # Here we use distinct client_ids from alerts as a proxy for "clients with risk"
                clients = db.query(SystemAlert.client_id).distinct().filter(SystemAlert.client_id != None).all()
                client_ids = [c[0] for c in clients]
                
                service = RiskService(db)
                for client_id in client_ids:
                    service.calculate_and_save_risk('client', client_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in Client Risk Watcher: {e}")
        
        await asyncio.sleep(600)
