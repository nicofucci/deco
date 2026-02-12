from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.risk.risk_service import RiskService
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

from datetime import datetime

class RiskScoreRead(BaseModel):
    id: str
    client_id: Optional[str]
    asset_id: Optional[str]
    agent_key: Optional[str]
    score_actual: float
    trend: str
    risk_24h: float
    risk_72h: float
    risk_7d: float
    category: str
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

@router.get("/summary", response_model=RiskScoreRead)
def get_global_risk(db: Session = Depends(get_db)):
    service = RiskService(db)
    risk = service.get_risk_score(id='global')
    if not risk:
        # Calculate on fly if not exists
        risk = service.calculate_and_save_risk('global', 'global')
    return risk

@router.get("/by-client", response_model=List[RiskScoreRead])
def get_client_risks(db: Session = Depends(get_db)):
    service = RiskService(db)
    # In a real app we would filter by client_id is not null
    # For now, we return all and frontend filters or we add specific query method
    all_risks = service.get_all_risks()
    return [r for r in all_risks if r.client_id]

@router.get("/by-assets", response_model=List[RiskScoreRead])
def get_asset_risks(db: Session = Depends(get_db)):
    service = RiskService(db)
    all_risks = service.get_all_risks()
    return [r for r in all_risks if r.asset_id]

@router.get("/agents", response_model=List[RiskScoreRead])
def get_agent_risks(db: Session = Depends(get_db)):
    service = RiskService(db)
    all_risks = service.get_all_risks()
    return [r for r in all_risks if r.agent_key]

@router.post("/recalculate")
def recalculate_risks(db: Session = Depends(get_db)):
    """Force recalculation of global risk"""
    service = RiskService(db)
    risk = service.calculate_and_save_risk('global', 'global')
    return {"status": "recalculated", "score": risk.score_actual}
