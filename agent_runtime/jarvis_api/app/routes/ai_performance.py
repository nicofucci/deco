from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.database import get_db
from app.services.ai_performance import AIPerformanceService

router = APIRouter(tags=["AI Performance"])

@router.get("/summary")
def get_performance_summary(db: Session = Depends(get_db)):
    """Obtiene resumen de rendimiento y KPIs globales."""
    service = AIPerformanceService(db)
    return service.get_performance_summary()

@router.get("/history/{agent_key}")
def get_agent_history(agent_key: str, limit: int = 50, db: Session = Depends(get_db)):
    """Obtiene historial de benchmarks para un agente."""
    service = AIPerformanceService(db)
    result = service.get_agent_history(agent_key, limit)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/ranking")
def get_ranking(db: Session = Depends(get_db)):
    """Obtiene ranking de agentes por desempeño."""
    service = AIPerformanceService(db)
    return service.get_ranking()
