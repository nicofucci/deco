"""
Utility functions for the API routers
"""
from datetime import datetime, timedelta, timezone
from app.models.domain import Agent

# Configuration
AGENT_OFFLINE_THRESHOLD_MINUTES = 5

def compute_agent_online_status(agent: Agent) -> str:
    """
    Calcula el status real del agente basándose en last_seen_at.
    
    Si el agente no ha enviado heartbeat en más de 5 minutos,
    se considera offline independientemente del status guardado.
    
    Args:
        agent: Instancia del modelo Agent
        
    Returns:
        str: "online", "idle", "offline", etc. (status real)
    """
    if not agent.last_seen_at:
        return "offline"
    
    threshold = datetime.now(timezone.utc) - timedelta(minutes=AGENT_OFFLINE_THRESHOLD_MINUTES)
    
    if agent.last_seen_at < threshold:
        return "offline"
    
    # Si está dentro del threshold, retornamos el status que reportó
    return agent.status or "offline"

def get_time_since_last_seen(agent: Agent) -> dict:
    """
    Calcula el tiempo transcurrido desde el último heartbeat.
    
    Returns:
        dict: {"seconds": int, "minutes": int, "is_offline": bool}
    """
    if not agent.last_seen_at:
        return {"seconds": None, "minutes": None, "is_offline": True}
    
    delta = datetime.now(timezone.utc) - agent.last_seen_at
    seconds = int(delta.total_seconds())
    minutes = seconds // 60
    is_offline = minutes >= AGENT_OFFLINE_THRESHOLD_MINUTES
    
    return {
        "seconds": seconds,
        "minutes": minutes,
        "is_offline": is_offline
    }
