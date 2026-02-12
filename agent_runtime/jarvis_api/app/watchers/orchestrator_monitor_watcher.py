import asyncio
import logging
import httpx
from app.database import SessionLocal
from app.services.alerts_service import create_alert_from_event

logger = logging.getLogger(__name__)

async def start_orchestrator_monitor_watcher():
    """
    Monitor Orchestrator API.
    Runs every 60 seconds.
    """
    logger.info("Starting Orchestrator Monitor Watcher...")
    while True:
        try:
            await check_orchestrator()
        except Exception as e:
            logger.error(f"Error in Orchestrator Monitor Watcher: {e}")
        
        await asyncio.sleep(60)

async def check_orchestrator():
    db = SessionLocal()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                # Orchestrator is usually at orchestrator_api:8000
                resp = await client.get("http://orchestrator_api:8000/health")
                if resp.status_code != 200:
                     create_alert_from_event(
                        db,
                        event_type="SYSTEM",
                        severity="high",
                        source="orchestrator_monitor",
                        title="Orchestrator Unhealthy",
                        description=f"Orchestrator returned status {resp.status_code}",
                        metadata={"status": resp.status_code}
                    )
            except Exception as e:
                create_alert_from_event(
                    db,
                    event_type="SYSTEM",
                    severity="high",
                    source="orchestrator_monitor",
                    title="Orchestrator Down",
                    description=f"Could not connect to Orchestrator: {str(e)}",
                    metadata={"error": str(e)}
                )
    finally:
        db.close()
