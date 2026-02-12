import asyncio
import logging
import psutil
import httpx
from app.database import SessionLocal
from app.services.alerts_service import create_alert_from_event
from app.services.action_service import ActionService

logger = logging.getLogger(__name__)

async def start_system_health_watcher():
    """
    Monitor System Health (CPU, RAM, Services).
    Runs every 60 seconds.
    """
    logger.info("Starting System Health Watcher...")
    while True:
        try:
            await check_system_health()
        except Exception as e:
            logger.error(f"Error in System Health Watcher: {e}")
        
        await asyncio.sleep(60)

async def check_system_health():
    db = SessionLocal()
    try:
        # 1. CPU & RAM
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent

        if cpu_percent > 90:
            create_alert_from_event(
                db,
                event_type="SYSTEM",
                severity="high",
                source="system_monitor",
                title="High CPU Usage",
                description=f"CPU usage is at {cpu_percent}% (Threshold: 90%)",
                metric_value=cpu_percent,
                threshold=90,
                metadata={"cpu": cpu_percent}
            )

        if ram_percent > 85:
            create_alert_from_event(
                db,
                event_type="SYSTEM",
                severity="warning",
                source="system_monitor",
                title="High Memory Usage",
                description=f"RAM usage is at {ram_percent}% (Threshold: 85%)",
                metric_value=ram_percent,
                threshold=85,
                metadata={"ram": ram_percent}
            )

        # 2. Service Health Checks
        services = {
            "qdrant": "http://qdrant:6333/collections", # Basic check
            "ollama": "http://ollama:11434/api/tags",
            "redis": None # Handled by redis_monitor_watcher usually, but we can do a basic check here or skip if redundant
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Qdrant
            try:
                resp = await client.get(services["qdrant"])
                if resp.status_code != 200:
                    raise Exception(f"Status {resp.status_code}")
            except Exception as e:
                # Create Alert
                alert = create_alert_from_event(
                    db=db,
                    event_type="SYSTEM", # Keep original event_type
                    source="system_monitor",
                    title="Qdrant Service Down",
                    description=f"Qdrant vector database is unreachable on port 6333: {str(e)}", # Updated description
                    severity="critical",
                    asset_id="qdrant",
                    metadata={"error": str(e)}
                )
                
                # Propose Action (Hybrid Mode - Auto Defense)
                action_service = ActionService(db)
                action_service.apply_auto_actions(
                    type="restart_service",
                    description="Restart Qdrant Container",
                    risk_level="medium",
                    source="system_health_watcher",
                    payload={"service": "qdrant"},
                    alert_id=alert.id
                )

            # Ollama
            try:
                resp = await client.get(services["ollama"])
                if resp.status_code != 200:
                    raise Exception(f"Status {resp.status_code}")
            except Exception as e:
                create_alert_from_event(
                    db,
                    event_type="SYSTEM",
                    severity="high",
                    source="system_monitor",
                    title="Ollama Service Down",
                    description=f"Ollama is unreachable: {str(e)}",
                    metadata={"error": str(e)}
                )

    finally:
        db.close()
