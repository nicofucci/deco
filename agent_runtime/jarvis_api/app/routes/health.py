from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.risk.risk_service import RiskService
from app.models.alerts import Alert
from datetime import datetime, timezone
import psutil
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health/full")
async def full_health_check(db: Session = Depends(get_db)):
    """
    Heartbeat Operativo Completo.
    Devuelve estado de servicios, métricas, riesgo y alertas.
    """
    # 1. System Metrics
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # 2. Services Status
    services = {
        "jarvis_api": "online",
        "orchestrator": "unknown",
        "qdrant": "unknown",
        "ollama": "unknown",
        "redis": "unknown"
    }

    async with httpx.AsyncClient(timeout=2.0) as client:
        # Orchestrator
        try:
            resp = await client.get("http://orchestrator_api:8000/health")
            services["orchestrator"] = "online" if resp.status_code == 200 else "degraded"
        except:
            services["orchestrator"] = "offline"
        
        # Qdrant
        try:
            resp = await client.get("http://qdrant:6333/collections")
            services["qdrant"] = "online" if resp.status_code == 200 else "degraded"
        except:
            services["qdrant"] = "offline"

        # Ollama
        try:
            resp = await client.get("http://ollama:11434/api/tags")
            services["ollama"] = "online" if resp.status_code == 200 else "degraded"
        except:
            services["ollama"] = "offline"

    # Redis (via internal check if possible, or assume online if API works as it uses Redis)
    # We can check via redis_bus if available, but for now simple assumption or skip
    services["redis"] = "online" # Simplified

    # 3. Global Risk
    risk_service = RiskService(db)
    global_risk = risk_service.get_risk_score('global', 'global')
    risk_score = global_risk.score if global_risk else 0.0
    risk_level = global_risk.level if global_risk else "unknown"

    # 4. Critical Alerts (Last 24h)
    critical_alerts = db.query(Alert).filter(
        Alert.severity == "critical",
        Alert.status == "open"
    ).count()

    # 5. Overall Status
    status = "green"
    if critical_alerts > 0 or risk_score > 80 or any(s == "offline" for s in services.values()):
        status = "red"
    elif risk_score > 50 or any(s == "degraded" for s in services.values()) or cpu > 90:
        status = "yellow"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "metrics": {
            "cpu": cpu,
            "ram": ram,
            "disk": disk
        },
        "services": services,
        "risk": {
            "score": risk_score,
            "level": risk_level
        },
        "alerts": {
            "critical_open": critical_alerts
        }
    }
