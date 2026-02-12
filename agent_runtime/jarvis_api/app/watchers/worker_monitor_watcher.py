import asyncio
import logging
import httpx
from app.database import SessionLocal
from app.services.alerts_service import create_alert_from_event

logger = logging.getLogger(__name__)

async def start_worker_monitor_watcher():
    """
    Monitor Background Workers (Pentest Worker, etc).
    Runs every 2 minutes.
    """
    logger.info("Starting Worker Monitor Watcher...")
    while True:
        try:
            await check_workers()
        except Exception as e:
            logger.error(f"Error in Worker Monitor Watcher: {e}")
        
        await asyncio.sleep(120)

async def check_workers():
    db = SessionLocal()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Pentest Worker
            try:
                resp = await client.get("http://pentest_worker:8082/health")
                if resp.status_code != 200:
                    create_alert_from_event(
                        db,
                        event_type="SYSTEM",
                        severity="high",
                        source="worker_monitor",
                        title="Pentest Worker Unhealthy",
                        description=f"Pentest worker returned status {resp.status_code}",
                        metadata={"worker": "pentest_worker", "status": resp.status_code}
                    )
            except Exception as e:
                create_alert_from_event(
                    db,
                    event_type="SYSTEM",
                    severity="critical",
                    source="worker_monitor",
                    title="Pentest Worker Down",
                    description=f"Could not connect to pentest_worker: {str(e)}",
                    metadata={"worker": "pentest_worker", "error": str(e)}
                )
    finally:
        db.close()
