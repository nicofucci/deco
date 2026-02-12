from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.ai_benchmarks import AIBenchmarkService
from app.services.agents_registry import get_all_agents

router = APIRouter(tags=["AI Agents Benchmarks"])

class BenchmarkRequest(BaseModel):
    agent_key: str
    runs: int = 3

@router.post("/benchmark")
async def run_benchmark(
    request: BenchmarkRequest,
    db: Session = Depends(get_db)
):
    """Ejecuta benchmarks para un agente o todos."""
    service = AIBenchmarkService(db)
    results = []
    
    if request.agent_key == "ALL":
        agents = get_all_agents()
        for agent in agents:
            res = await service.run_benchmark(agent.key, request.runs)
            results.append(res)
    else:
        res = await service.run_benchmark(request.agent_key, request.runs)
        if "error" in res:
            raise HTTPException(status_code=404, detail=res["error"])
        results.append(res)
        
    return {
        "started_at": datetime.now().isoformat(), # Approx
        "finished_at": datetime.now().isoformat(),
        "total_agents": len(results),
        "total_runs": sum(r["runs"] for r in results),
        "results": results
    }

@router.get("/benchmark/summary")
def get_benchmark_summary(db: Session = Depends(get_db)):
    """Obtiene resumen histórico de benchmarks."""
    service = AIBenchmarkService(db)
    return service.get_summary()

@router.get("/benchmark/history/{agent_key}")
def get_benchmark_history(agent_key: str, limit: int = 50, db: Session = Depends(get_db)):
    """Obtiene historial detallado de un agente."""
    service = AIBenchmarkService(db)
    history = service.get_history(agent_key, limit)
    if not history:
        raise HTTPException(status_code=404, detail="Agente no encontrado o sin datos")
    return history
