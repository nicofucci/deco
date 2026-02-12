
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db
from app.models.domain import AgentStatus, FleetAlert, Agent

router = APIRouter()

@router.get("/agents")
def get_fleet_agents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None, # healthy, warning, critical
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_active_user) # Assuming Master/Admin Auth
):
    """
    Global Fleet View (Master Console)
    """
    query = db.query(AgentStatus)
    
    if status:
        query = query.filter(AgentStatus.health_state == status)
        
    total = query.count()
    agents = query.order_by(desc(AgentStatus.last_seen)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": agents
    }

@router.get("/agents/{agent_id}")
def get_agent_details(
    agent_id: str,
    db: Session = Depends(get_db)
):
    status = db.query(AgentStatus).filter(AgentStatus.agent_id == agent_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Agent Status not found")
    
    # Get active alerts
    alerts = db.query(FleetAlert).filter(
        FleetAlert.agent_id == agent_id,
        FleetAlert.resolved == False
    ).all()
    
    return {
        "status": status,
        "alerts": alerts
    }

@router.get("/alerts")
def get_global_alerts(
    resolved: bool = False,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Global Alerts View
    """
    query = db.query(FleetAlert).filter(FleetAlert.resolved == resolved)
    
    if severity:
        query = query.filter(FleetAlert.severity == severity)
        
    return query.order_by(desc(FleetAlert.timestamp)).all()

# Client Specific Endpoints (for Partner Console)

@router.get("/clients/{client_id}/agents")
def get_client_fleet(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Client Fleet View
    """
    # Single Source of Truth: Agent table
    # We join with AgentStatus to get runtime info, but we MUST return all agents
    from app.models.domain import Agent
    
    results = db.query(Agent, AgentStatus).outerjoin(
        AgentStatus, Agent.id == AgentStatus.agent_id
    ).filter(
        Agent.client_id == client_id
    ).all()

    fleet_view = []
    for agent, status in results:
        if status:
            fleet_view.append(status)
        else:
            # Synthetic status for agents that haven't reported yet (or lost status)
            # This ensures consistency with "My Clients" count
            fleet_view.append({
                "agent_id": agent.id,
                "client_id": agent.client_id,
                "hostname": agent.hostname,
                "ip": agent.ip or agent.local_ip,
                "platform": agent.os or "unknown",
                "version": agent.version,
                "health_state": "unknown", # Explicitly mark as unknown
                "last_seen": agent.last_seen_at,
                "last_update_status": "unknown",
                "jobs_executed_24h": 0,
                "jobs_failed_24h": 0,
                "cpu_usage": 0.0,
                "ram_usage": 0.0,
                "error_reason": "No heartbeat received yet"
            })
            
    return fleet_view

@router.get("/clients/{client_id}/alerts")
def get_client_alerts(
    client_id: str,
    db: Session = Depends(get_db)
):
    alerts = db.query(FleetAlert).filter(
        FleetAlert.client_id == client_id,
        FleetAlert.resolved == False
    ).all()
    return alerts

@router.get("/updates/check")
def check_for_updates(
    platform: str,
    current_version: str,
    arch: Optional[str] = "amd64",
    db: Session = Depends(get_db)
):
    """
    Agent Update Check
    """
    from app.models.domain import AgentVersion
    
    # Find latest stable version for platform
    latest = (
        db.query(AgentVersion)
        .filter(AgentVersion.platform == platform, AgentVersion.tier == "stable")
        .order_by(desc(AgentVersion.release_date))
        .first()
    )
    
    if not latest:
        return {"update_available": False}
        
    # Simple version comparison (inexact if not using semver lib, but sufficient for now)
    # Ideally: use packaging.version.parse
    if latest.version != current_version:
         return {
            "update_available": True,
            "version": latest.version,
            "url": latest.download_url,
            "checksum": latest.checksum_sha256,
            "force": latest.is_forced,
            "changelog": latest.changelog
        }
        
    return {"update_available": False}
