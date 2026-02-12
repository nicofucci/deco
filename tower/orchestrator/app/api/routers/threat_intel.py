
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.db.session import get_db
from app.models.domain import GlobalThreat, ClientThreatMatch, NetworkAsset
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# --- Schemas ---

class GlobalThreatRead(BaseModel):
    id: str
    source: str
    cve: str
    title: str
    description: Optional[str]
    published_at: Optional[datetime]
    tags: List[str]
    exploit_status: str
    risk_score_base: float
    created_at: datetime
    
    class Config:
        orm_mode = True

class ClientMatchRead(BaseModel):
    id: str
    threat_id: str
    cve: str
    title: str
    asset_ip: Optional[str]
    asset_hostname: Optional[str]
    match_reason: str
    risk_level: str
    status: str
    
    class Config:
        orm_mode = True

class ThreatSummary(BaseModel):
    total_threats: int
    critical_matches: int
    zero_days_count: int

# --- Endpoints ---

@router.get("/global", response_model=List[GlobalThreatRead])
def get_global_threats(limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns latest global threats.
    """
    threats = db.query(GlobalThreat).order_by(desc(GlobalThreat.published_at)).limit(limit).all()
    return threats

@router.get("/clients/{client_id}/matches", response_model=List[ClientMatchRead])
def get_client_threat_matches(client_id: str, db: Session = Depends(get_db)):
    """
    Returns threats that match this client's assets.
    """
    matches = db.query(ClientThreatMatch).filter(
        ClientThreatMatch.client_id == client_id,
        ClientThreatMatch.status == "active"
    ).all()
    
    # Enrich with threat info manually or via join if needed easier in schema
    # For now, construct response
    result = []
    for m in matches:
        threat = m.threat
        asset = m.asset
        result.append({
            "id": m.id,
            "threat_id": m.threat_id,
            "cve": threat.cve,
            "title": threat.title,
            "asset_ip": asset.ip if asset else "Unknown",
            "asset_hostname": asset.hostname if asset else "Unknown",
            "match_reason": m.match_reason,
            "risk_level": m.risk_level,
            "status": m.status
        })
    return result

@router.get("/clients/{client_id}/summary", response_model=ThreatSummary)
def get_client_threat_summary(client_id: str, db: Session = Depends(get_db)):
    """
    Returns summary for dashboard widgets.
    """
    total = db.query(ClientThreatMatch).filter(
        ClientThreatMatch.client_id == client_id,
        ClientThreatMatch.status == "active"
    ).count()
    
    critical = db.query(ClientThreatMatch).filter(
        ClientThreatMatch.client_id == client_id,
        ClientThreatMatch.status == "active",
        ClientThreatMatch.risk_level == "critical"
    ).count()
    
    # Zero days? Maybe tag check on GlobalThreat joined
    # For simplicity, count criticals with "exploit" match reason or high risk base
    # Correct logic: Join ClientThreatMatch -> GlobalThreat -> Check tags
    # Implementation later for strict tags
    
    return {
        "total_threats": total,
        "critical_matches": critical,
        "zero_days_count": 0 # Placeholder for advanced tag filtering
    }
