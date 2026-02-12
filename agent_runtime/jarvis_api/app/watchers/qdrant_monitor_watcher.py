import asyncio
import logging
import httpx
from app.database import SessionLocal
from app.services.alerts_service import create_alert_from_event

logger = logging.getLogger(__name__)

async def start_qdrant_monitor_watcher():
    """
    Monitor Qdrant Vector DB.
    Runs every 60 seconds.
    """
    logger.info("Starting Qdrant Monitor Watcher...")
    while True:
        try:
            await check_qdrant()
        except Exception as e:
            logger.error(f"Error in Qdrant Monitor Watcher: {e}")
        
        await asyncio.sleep(60)

async def check_qdrant():
    db = SessionLocal()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get("http://qdrant:6333/healthz")
                # Qdrant healthz returns 200 OK or body
                if resp.status_code != 200:
                     create_alert_from_event(
                        db,
                        event_type="SYSTEM",
                        severity="critical",
                        source="qdrant_monitor",
                        title="Qdrant Unhealthy",
                        description=f"Qdrant returned status {resp.status_code}",
                        metadata={"status": resp.status_code}
                    )
            except Exception as e:
                create_alert_from_event(
                    db,
                    event_type="SYSTEM",
                    severity="critical",
                    source="qdrant_monitor",
                    title="Qdrant Down",
                    description=f"Could not connect to Qdrant: {str(e)}",
                    metadata={"error": str(e)}
                )
    finally:
        db.close()
