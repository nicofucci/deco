from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.api.deps import get_db
from app.models.domain import AgentVersion, Agent

router = APIRouter()

class UpdateMetadataResponse(BaseModel):
    update_available: bool
    forced: bool
    latest_version: Optional[str] = None
    download_url: Optional[str] = None
    sha256: Optional[str] = None
    changelog: Optional[str] = None

class UpdateStatusRequest(BaseModel):
    previous_version: str
    new_version: str
    status: str # success, failed
    message: Optional[str] = None

@router.get("/update-metadata", response_model=UpdateMetadataResponse)
def check_for_updates(
    platform: str,
    current_version: str,
    agent_id: Optional[str] = None, # Optional tracking
    db: Session = Depends(get_db)
):
    """
    Checks for the latest available version for the given platform.
    """
    # 1. Get latest version for platform
    latest = db.query(AgentVersion).filter(
        AgentVersion.platform == platform,
        AgentVersion.tier == "stable" # En el futuro soportar kanares/beta
    ).order_by(desc(AgentVersion.release_date)).first()

    if not latest:
        return {
            "update_available": False,
            "forced": False
        }

    # 2. Compare versions (Naive string comparison for v1, semver lib better for v2)
    # Assuming exact match update loop prevention
    if latest.version == current_version:
        return {
            "update_available": False,
            "forced": False
        }

    return {
        "update_available": True,
        "forced": latest.is_forced,
        "latest_version": latest.version,
        "download_url": latest.download_url,
        "sha256": latest.checksum_sha256,
        "changelog": latest.changelog
    }

@router.get("/releases/latest")
def get_latest_release_simple(
    channel: str = "stable",
    platform: str = "windows",
    db: Session = Depends(get_db)
):
    """
    Simple endpoint for Latest Release info.
    """
    latest = db.query(AgentVersion).filter(
        AgentVersion.platform == platform,
        AgentVersion.tier == channel
    ).order_by(desc(AgentVersion.release_date)).first()

    if not latest:
        raise HTTPException(status_code=404, detail="No release found")

    return {
        "version": latest.version,
        "url": latest.download_url,
        "sha256": latest.checksum_sha256,
        "created_at": latest.release_date
    }

@router.post("/{agent_id}/update-status")
def report_update_status(
    agent_id: str,
    payload: UpdateStatusRequest,
    db: Session = Depends(get_db)
):
    """
    Reports the result of an update attempt.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Simple logging / future timeline implementation
    # For now, just print or log to a simple audit table if we had one.
    # We can update the agent version directly if success.
    
    if payload.status == "success":
        agent.version = payload.new_version
        
        # Check if version exists in DB, if not maybe dynamic registration (not rec)
        # Assuming version exists.
        
    db.commit()
    
    return {"status": "recorded"}

