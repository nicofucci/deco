from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.predictive_engine import PredictiveEngine, PredictiveReport
from app.models.domain import Client, PredictiveSignal
from typing import List, Optional
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger("DecoOrchestrator.API.Predictive")

class PredictiveSignalSchema(BaseModel):
    id: Optional[str] = None
    signal_type: str
    severity: str
    description: str
    score_delta: int
    created_at: Optional[str] = None # simplified datetime

class PredictiveResponse(BaseModel):
    score: int
    signals: List[PredictiveSignalSchema]

@router.get("/clients/{client_id}/predictive", response_model=PredictiveResponse)
def get_predictive_report(client_id: str, db: Session = Depends(get_db)):
    """
    Returns the current predictive risk score and active signals.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    signals = db.query(PredictiveSignal).filter(PredictiveSignal.client_id == client_id).all()
    
    # Map to schema
    sig_schemas = [
        PredictiveSignalSchema(
            id=s.id,
            signal_type=s.signal_type,
            severity=s.severity,
            description=s.description or "",
            score_delta=s.score_delta or 0,
            created_at=str(s.created_at)
        ) for s in signals
    ]
    
    # If no score set (default 100), it's 100.
    return PredictiveResponse(
        score=client.predictive_risk_score if client.predictive_risk_score is not None else 100,
        signals=sig_schemas
    )

@router.post("/clients/{client_id}/predictive/analyze", response_model=PredictiveResponse)
def trigger_analysis(client_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers an immediate predictive analysis.
    """
    engine = PredictiveEngine(db)
    report = engine.analyze_client(client_id)
    
    # Map response
    sig_schemas = [
        PredictiveSignalSchema(
             signal_type=s["type"],
             severity=s["severity"],
             description=s["description"],
             score_delta=s.get("score_delta", 0)
        ) for s in report.signals
    ]
    
    return PredictiveResponse(score=report.score, signals=sig_schemas)
