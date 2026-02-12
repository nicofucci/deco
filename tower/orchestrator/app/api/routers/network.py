from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db
from app.models.domain import NetworkAsset, Client, NetworkObservation
from app.schemas.contracts import ClientNetworkAssetResponse
import logging

logger = logging.getLogger("orchestrator")

router = APIRouter()

from app.schemas.contracts import NetworkObservationSchema
from app.services.network_fusion_service import fuse_observations

@router.get("/clients/{client_id}/network-assets", response_model=List[ClientNetworkAssetResponse])
def get_client_network_assets(
    client_id: str,
    scope: str = Query("lan", regex="^(lan|all)$"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de activos de red descubiertos.
    scope=lan (default): Oculta docker/loopback/link-local.
    scope=all: Muestra todo.
    """
    # Verificar si el cliente existe
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    query = db.query(NetworkAsset).filter(NetworkAsset.client_id == client_id)
    
    if scope == "lan":
        # Filter out local_interface, loopback, link_local
        # Assuming origin_type is populated. If null/unknown, we include it to be safe or exclude?
        # Safe to include unknown, but exclude explicit noise.
        query = query.filter(NetworkAsset.origin_type.notin_(["local_interface", "loopback", "link_local"]))
        
    assets = query.all()
    return assets

@router.post("/clients/{client_id}/observations", status_code=202)
def ingest_network_observations(
    client_id: str,
    observations: List[NetworkObservationSchema],
    db: Session = Depends(get_db)
):
    """
    Recibe observaciones crudas del sensor NDR y las fusiona.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
         
    try:
        fuse_observations(client_id, observations, db)
        return {"status": "ok", "processed": len(observations)}
    except Exception as e:
        logger.error(f"Ingest Error: {e}")
        # Return error but 500
        raise HTTPException(status_code=500, detail=str(e))


from sqlalchemy import or_

@router.get("/clients/{client_id}/network-assets/{asset_id}/evidence", response_model=List[NetworkObservationSchema])
def get_asset_evidence(
    client_id: str,
    asset_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Returns latest raw observations (evidence) for an asset.
    """
    asset = db.query(NetworkAsset).filter(
        NetworkAsset.id == asset_id, 
        NetworkAsset.client_id == client_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    query = db.query(NetworkObservation).filter(NetworkObservation.client_id == client_id)
    
    conditions = []
    if asset.mac: conditions.append(NetworkObservation.mac == asset.mac)
    if asset.ip: conditions.append(NetworkObservation.ip == asset.ip)
    
    if conditions:
        query = query.filter(or_(*conditions))
    else:
        return []
        
    return query.order_by(NetworkObservation.timestamp.desc()).limit(limit).all()


# =========================
# VULNERABILITY ENDPOINTS (Task 1.2)
# =========================

from app.models.domain import NetworkVulnerability
from app.schemas.contracts import VulnerabilityEntry, EnrichedAssetVulnerabilities

@router.get("/clients/{client_id}/vulnerabilities", response_model=List[VulnerabilityEntry])
def get_client_vulnerabilities(
    client_id: str,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all vulnerabilities for a client, optionally filtered by severity.
    """
    query = db.query(NetworkVulnerability).filter(NetworkVulnerability.client_id == client_id)
    
    if severity:
        query = query.filter(NetworkVulnerability.severity == severity.lower())
        
    vulns = query.all()
    return vulns

@router.get("/clients/{client_id}/network-assets/{asset_id}/vulnerabilities", response_model=EnrichedAssetVulnerabilities)
def get_asset_vulnerabilities(
    client_id: str,
    asset_id: str,
    db: Session = Depends(get_db)
):
    """
    Get vulnerabilities for a specific asset.
    """
    asset = db.query(NetworkAsset).filter(
        NetworkAsset.id == asset_id, 
        NetworkAsset.client_id == client_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    vulns = db.query(NetworkVulnerability).filter(NetworkVulnerability.asset_id == asset_id).all()
    
    # Calculate aggregates
    total_score = sum([v.cvss_score for v in vulns])
    critical_count = len([v for v in vulns if v.severity == "critical"])
    high_count = len([v for v in vulns if v.severity == "high"])
    
    return EnrichedAssetVulnerabilities(
        asset_id=asset.id,
        ip=asset.ip,
        hostname=asset.hostname,
        vulnerabilities=vulns,
        total_score=total_score,
        critical_count=critical_count,
        high_count=high_count
    )

@router.get("/clients/{client_id}/vulnerabilities/critical", response_model=List[VulnerabilityEntry])
def get_client_critical_vulnerabilities(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Shortcut to get only Critical vulnerabilities.
    """
    vulns = db.query(NetworkVulnerability).filter(
        NetworkVulnerability.client_id == client_id,
        NetworkVulnerability.severity == "critical"
    ).all()
    return vulns


# =========================
# SPECIALIZED DEEP SCANS (Task 1.3)
# =========================

from app.models.domain import SpecializedFinding, ScanJob, Agent
from app.schemas.contracts import SpecializedFindingResponse, SpecializedJobRequest, ScanJobResponse
import uuid

@router.get("/clients/{client_id}/specialized-findings", response_model=List[SpecializedFindingResponse])
def get_specialized_findings(
    client_id: str,
    asset_id: Optional[str] = None,
    job_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get specialized findings (IoT, SMB, Fingerprint) for a client.
    Optionally filter by asset_id or job_type.
    """
    # Join with NetworkAsset to ensure client ownership
    query = (
        db.query(SpecializedFinding)
        .join(NetworkAsset)
        .filter(NetworkAsset.client_id == client_id)
    )

    if asset_id:
        query = query.filter(SpecializedFinding.asset_id == asset_id)
    
    if job_type:
        query = query.filter(SpecializedFinding.job_type == job_type)

    return query.all()

def _trigger_specialized_job(
    client_id: str, 
    job_type: str, 
    request: SpecializedJobRequest, 
    db: Session
):
    # Verify asset exists
    asset = db.query(NetworkAsset).filter(
        NetworkAsset.client_id == client_id,
        NetworkAsset.ip == request.target_ip
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {request.target_ip} not found. Scan it with X-RAY first.")

    # Determine Agent (Asset's last agent or a generic online agent for client)
    agent_id = request.agent_id or asset.agent_id
    if not agent_id:
        # Fallback: Find any online agent for this client
        agent = db.query(Agent).filter(
            Agent.client_id == client_id,
            Agent.status == "online"
        ).first()
        if not agent:
             raise HTTPException(status_code=400, detail="No online agent found to execute scan.")
        agent_id = agent.id

    job = ScanJob(
        id=str(uuid.uuid4()),
        client_id=client_id,
        agent_id=agent_id,
        type=job_type,
        target=request.target_ip,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.post("/clients/{client_id}/jobs/iot-deep-scan", response_model=ScanJobResponse)
def trigger_iot_deep_scan(
    client_id: str,
    request: SpecializedJobRequest,
    db: Session = Depends(get_db)
):
    return _trigger_specialized_job(client_id, "iot_deep_scan", request, db)

@router.post("/clients/{client_id}/jobs/smb-rdp-audit", response_model=ScanJobResponse)
def trigger_smb_rdp_audit(
    client_id: str,
    request: SpecializedJobRequest,
    db: Session = Depends(get_db)
):
    return _trigger_specialized_job(client_id, "smb_rdp_audit", request, db)

@router.post("/clients/{client_id}/jobs/critical-fingerprint", response_model=ScanJobResponse)
def trigger_critical_fingerprint(
    client_id: str,
    request: SpecializedJobRequest,
    db: Session = Depends(get_db)
):
    return _trigger_specialized_job(client_id, "critical_service_fingerprint", request, db)


# =========================
# ASSET ACTIVITY TRACKING (Task 1.4)
# =========================

from pydantic import BaseModel
class NetworkAssetSummary(BaseModel):
    total: int
    active: int
    new_assets: int # 'new' is keyword
    stable: int
    gone: int
    at_risk: int

@router.get("/clients/{client_id}/network-assets/summary", response_model=NetworkAssetSummary)
def get_network_assets_summary(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns counts of assets by status for the activity dashboard.
    """
    assets = db.query(NetworkAsset).filter(NetworkAsset.client_id == client_id).all()
    
    summary = {
        "total": len(assets),
        "active": 0, # Calculated based on last_seen < 24h? Or just 'active' status if we had it. Use implicit logic.
        "new_assets": 0,
        "stable": 0,
        "gone": 0,
        "at_risk": 0
    }
    
    now = datetime.now(timezone.utc)
    
    for a in assets:
        summary["new_assets"] += 1 if a.status == "new" else 0
        summary["stable"] += 1 if a.status == "stable" else 0
        summary["gone"] += 1 if a.status == "gone" else 0
        summary["at_risk"] += 1 if a.status == "at_risk" else 0
        
        # "Active" definition for UI: Seen in last 24 hours AND not gone
        if a.status != "gone" and a.last_seen:
            # handle timezone awareness
            if a.last_seen.tzinfo:
                delta = now - a.last_seen
            else:
                delta = now.replace(tzinfo=None) - a.last_seen
                
            if delta.total_seconds() < 86400: # 24 hours
                summary["active"] += 1

    return summary

from app.models.domain import NetworkAssetHistory

class AssetHistoryEntry(BaseModel):
    date: datetime
    status: Optional[str]
    reason: Optional[str]
    ip: Optional[str]
    
    class Config:
        orm_mode = True

@router.get("/clients/{client_id}/network-assets/{asset_id}/history", response_model=List[AssetHistoryEntry])
def get_asset_history(
    client_id: str,
    asset_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns history of status changes for a specific asset.
    """
    history = db.query(NetworkAssetHistory).filter(
        NetworkAssetHistory.asset_id == asset_id
    ).order_by(NetworkAssetHistory.date.desc()).all()
    
    # Map 'changed_at' to 'date' if 'date' is old? 
    # The Model has 'date' and 'changed_at'. The migration added 'changed_at' but 'date' exists.
    # We'll return 'changed_at' as 'date' in the schema if available, or just rely on 'date'.
    # For now, let's trust the ORM mapping.
    
    return history

