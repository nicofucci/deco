from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.action_service import ActionService
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()

class ActionRead(BaseModel):
    id: str
    type: str
    source_alert_id: Optional[str]
    description: str
    risk_level: str
    recommended_by: str
    status: str
    payload: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    executed_at: Optional[datetime]
    executed_by: Optional[str]

    class Config:
        orm_mode = True

@router.get("/pending", response_model=List[ActionRead])
def get_pending_actions(db: Session = Depends(get_db)):
    service = ActionService(db)
    return service.get_pending_actions()

@router.post("/{id}/approve", response_model=ActionRead)
def approve_action(id: str, db: Session = Depends(get_db)):
    service = ActionService(db)
    try:
        # Hardcoded operator for now
        action = service.approve_action(id, operator="Nicolas")
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        return action
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/reject", response_model=ActionRead)
def reject_action(id: str, db: Session = Depends(get_db)):
    service = ActionService(db)
    action = service.reject_action(id, operator="Nicolas")
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action

@router.post("/{id}/execute", response_model=ActionRead)
def execute_action(id: str, db: Session = Depends(get_db)):
    service = ActionService(db)
    try:
        action = service.execute_action(id, operator="Nicolas")
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        return action
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
