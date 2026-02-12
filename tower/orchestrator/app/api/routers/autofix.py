from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.api.deps import get_db, get_client_from_api_key, get_client_from_panel_key
from app.models.domain import Client, AutofixPlaybook, AutofixExecution
from app.services.autofix_engine import AutofixEngine

router = APIRouter()

# --- PARTNER / MASTER ENDPOINTS (Use Panel Key or Master Key effectively) ---
# For simplicity, we assume Master/Partner context via implicit trust or expanded auth in future.
# Here we use get_db and path params.

@router.post("/clients/{client_id}/autofix/generate")
def generate_client_playbooks(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Triggers the generation of draft playbooks for a client.
    """
    engine = AutofixEngine(db)
    generated = engine.generate_playbooks_for_client(client_id)
    return {"status": "ok", "generated_count": len(generated)}

@router.get("/clients/{client_id}/autofix/playbooks")
def list_client_playbooks(
    client_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lists playbooks for a client.
    """
    query = db.query(AutofixPlaybook).filter(AutofixPlaybook.client_id == client_id)
    if status:
        query = query.filter(AutofixPlaybook.status == status)
    
    return query.all()

@router.post("/autofix/playbooks/{playbook_id}/approve")
def approve_playbook(
    playbook_id: str,
    db: Session = Depends(get_db)
):
    """
    Approves a playbook for execution.
    """
    engine = AutofixEngine(db)
    success = engine.approve_playbook(playbook_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot approve playbook (Not found or not draft)")
    return {"status": "approved"}

@router.post("/autofix/playbooks/{playbook_id}/reject")
def reject_playbook(
    playbook_id: str,
    db: Session = Depends(get_db)
):
    """
    Rejects a playbook.
    """
    pb = db.query(AutofixPlaybook).filter(AutofixPlaybook.id == playbook_id).first()
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    pb.status = "rejected"
    db.commit()
    return {"status": "rejected"}

@router.post("/autofix/playbooks/{playbook_id}/execute")
def execute_playbook(
    playbook_id: str,
    db: Session = Depends(get_db)
):
    """
    Executes an approved playbook (Creates Agent Job).
    """
    engine = AutofixEngine(db)
    try:
        execution = engine.execute_playbook(playbook_id)
        return {
            "status": "pending", 
            "execution_id": execution.id, 
            "job_status": "dispatched"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
