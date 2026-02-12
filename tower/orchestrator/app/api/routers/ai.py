from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.ai_engine import ai_engine
from pydantic import BaseModel

router = APIRouter(tags=["ai"])

class PredictRequest(BaseModel):
    severity: str
    title: str = "Unknown"

@router.post("/train")
def train_model(db: Session = Depends(get_db)):
    """
    Entrena el modelo de IA con los datos actuales de la base de datos.
    """
    result = ai_engine.train()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.post("/predict")
def predict_risk(req: PredictRequest):
    """
    Predice el riesgo de un hallazgo basado en el modelo entrenado.
    """
    return ai_engine.predict(req.severity)


@router.get("/recommendations", response_model=list[Any])
def get_recommendations():
    """
    Devuelve recomendaciones de IA predictiva (Simuladas por ahora).
    """
    from datetime import date
    return [
        {
            "cliente": "AcmeCorp",
            "tipo": "Patrón sospechoso de tráfico SMB",
            "recomendacion": "Revisar acceso remoto y reforzar autenticación en 192.168.100.85",
            "probabilidad": 0.91,
            "fecha": str(date.today())
        },
        {
            "cliente": "TechSolutions",
            "tipo": "Anomalía en puertos salientes",
            "recomendacion": "Bloquear puerto 445 hacia IP externa desconocida",
            "probabilidad": 0.85,
            "fecha": str(date.today())
        },
        {
            "cliente": "GlobalFinance",
            "tipo": "Vulnerabilidad crítica recurrente",
            "recomendacion": "Aplicar parche MS17-010 en servidores legacy",
            "probabilidad": 0.98,
            "fecha": str(date.today())
        }
    ]
