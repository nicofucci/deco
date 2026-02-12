from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.alerts import AlertCreate, AlertRead, AlertUpdateStatus
from app.services import alerts_service

router = APIRouter()

@router.get("/", response_model=List[AlertRead])
def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    type: Optional[str] = Query(None, description="Filter by type"),
    agent_key: Optional[str] = Query(None, description="Filter by agent_key"),
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List system alerts with optional filtering.
    """
    return alerts_service.list_alerts(
        db, 
        status=status, 
        severity=severity, 
        type=type, 
        agent_key=agent_key,
        limit=limit,
        offset=offset
    )

@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Get a specific alert by ID.
    """
    alert = alerts_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/", response_model=AlertRead)
def create_alert(alert_data: AlertCreate, db: Session = Depends(get_db)):
    """
    Create a new system alert manually.
    """
    return alerts_service.create_alert(db, alert_data)

@router.patch("/{alert_id}/status", response_model=AlertRead)
def update_alert_status(alert_id: str, status_update: AlertUpdateStatus, db: Session = Depends(get_db)):
    """
    Update the status of an alert.
    """
    alert = alerts_service.update_alert_status(db, alert_id, status_update.status)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/{alert_id}/apply-remediation")
async def apply_remediation(alert_id: str, db: Session = Depends(get_db)):
    """
    Apply the recommended remediation for an alert.
    """
    try:
        from app.services.deco_supervisor import DecoSupervisor
        # User ID hardcoded for now or extracted from context if auth existed
        user_id = "manual_user" 
        result = await DecoSupervisor.execute_remediation(alert_id, user_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log error
        import logging
        logging.getLogger(__name__).error(f"Remediation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
