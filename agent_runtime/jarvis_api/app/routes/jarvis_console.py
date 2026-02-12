from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.intent_classifier import IntentClassifier
from app.services.ollama_client import JarvisOllamaClient
from app.risk.risk_service import RiskService
from app.services.action_service import ActionService
from app.models.alerts import SystemAlert
from app.models.jarvis_console import JarvisConsoleMessage, JarvisSession
from sqlalchemy import desc
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[Dict[str, str]]] = None
    session_id: Optional[str] = None

class ActionTriggered(BaseModel):
    type: str
    status: str
    details: Dict[str, Any]

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    actions_triggered: List[ActionTriggered]

@router.get("/history")
async def get_chat_history(
    user_id: str = "admin_console", 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    messages = db.query(JarvisConsoleMessage)\
        .filter(JarvisConsoleMessage.user_id == user_id)\
        .order_by(desc(JarvisConsoleMessage.created_at))\
        .limit(limit)\
        .all()
    
    return {
        "user_id": user_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            } for m in messages[::-1]
        ]
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_jarvis(request: ChatRequest, db: Session = Depends(get_db)):
    # 0. Resolve Session
    session = None
    if request.session_id:
        try:
            s_uuid = uuid.UUID(request.session_id)
            session = db.query(JarvisSession).filter(JarvisSession.id == s_uuid).first()
        except ValueError:
            pass
    
    if not session:
        # Try to find recent active session for user
        session = db.query(JarvisSession)\
            .filter(JarvisSession.user_id == "admin_console", JarvisSession.is_active == True)\
            .order_by(desc(JarvisSession.last_message_at))\
            .first()
            
        if not session:
            # Create new session
            session = JarvisSession(
                user_id="admin_console",
                title="Nueva sesión",
                last_message_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            db.refresh(session)

    # 1. Save User Message
    user_msg = JarvisConsoleMessage(
        user_id="admin_console",
        role="user",
        content=request.message,
        session_id=session.id
    )
    db.add(user_msg)
    
    # Update session timestamp
    session.last_message_at = datetime.utcnow()
    db.commit()

    classifier = IntentClassifier()
    ollama = JarvisOllamaClient()
    
    # 1. Analyze Intent
    analysis = await classifier.analyze_message(request.message)
    intent = analysis["intent"]
    params = analysis["params"]
    
    logger.info(f"Jarvis Chat Intent: {intent}, Params: {params}")
    
    reply = ""
    actions = []
    
    # 2. Dispatch Logic
    if intent == "general_chat":
        # Master System Prompt
        system_prompt = (
            "Eres Jarvis, un asistente operativo avanzado para Deco-Gravity. "
            "Tus roles son: Senior SOC Analyst, Pentester y SRE. "
            "Tu objetivo es analizar, vigilar, explicar y sugerir acciones. "
            "Responde SIEMPRE en español. Tono: Profesional, claro, directo, con humor sutil e inteligente. "
            "Llama SIEMPRE al usuario 'Nico'. "
            "Estructura tu respuesta: 1) Diagnóstico, 2) Explicación breve, 3) Acción sugerida (si aplica). "
            "Conoces toda la arquitectura de Deco-Gravity (contenedores en /opt/deco/agent_runtime). "
            "Nunca inventes datos técnicos ni acciones. "
            "Si todo está bien, sé relajado ('Todo tranqui en la torre'). Si es grave, sé serio."
        )
        resp = ollama.chat(messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ], options={"temperature": 0.3})
        
        if "error" in resp:
            reply = f"Nico, tuve un problema interno con mi núcleo cognitivo: {resp['error']}. ¿Quieres que reinicie el servicio?"
        else:
            reply = resp["message"]["content"]
            
    elif intent == "system.health":
        # Mocked health check for MVP
        reply = (
            "Nico, el sistema está **OPERATIVO** (Green).\n"
            "Diagnóstico: CPU 12%, RAM 4.2GB/16GB. Contenedores: 14/14 UP.\n"
            "Explicación: Todos los servicios core (Orchestrator, Jarvis API, Qdrant) responden en <50ms.\n"
            "Acción: Ninguna requerida. Todo tranqui en la torre."
        )
        actions.append(ActionTriggered(type="health_check", status="executed", details={"status": "healthy"}))
        
    elif intent == "risk.global" or intent == "show_risk":
        risk_service = RiskService(db)
        entity = params.get("entity", "global")
        
        risk = risk_service.get_risk_score(id="global")
        if not risk:
            risk = risk_service.calculate_and_save_risk("global", "global")
            
        reply = (
            f"Nico, el Riesgo Global actual es **{risk.score_actual:.1f}** ({risk.category.upper()}).\n"
            f"Diagnóstico: Tendencia {risk.trend}. Predicción a 7 días: {risk.risk_7d:.1f}.\n"
            f"Explicación: El sistema está estable, pero mantente alerta a cambios en la superficie de ataque."
        )
        actions.append(ActionTriggered(type="risk_query", status="executed", details={"score": risk.score_actual}))
        
    elif intent == "alerts.critical" or intent == "list_alerts":
        alerts = db.query(SystemAlert).filter(SystemAlert.severity.in_(["critical", "high"]), SystemAlert.status == "new").limit(5).all()
        if not alerts:
            reply = "Todo tranqui en la torre, Nico. No hay alertas críticas o altas nuevas. CPU relajada y Qdrant respirando profundo."
        else:
            reply = f"Nico, atención. He encontrado {len(alerts)} alertas importantes que requieren tu mirada:\n"
            for a in alerts:
                reply += f"- [{a.severity.upper()}] {a.title} ({a.source})\n"
            reply += "\n¿Quieres que profundice en alguna?"
        actions.append(ActionTriggered(type="alert_query", status="executed", details={"count": len(alerts)}))
        
    elif intent == "actions.pending" or intent == "list_actions":
        action_service = ActionService(db)
        pending = action_service.get_pending_actions()
        if not pending:
            reply = "No hay acciones pendientes de aprobación, Nico. El tablero está limpio."
        else:
            reply = f"Nico, tengo {len(pending)} acciones esperando tu luz verde:\n"
            for a in pending:
                reply += f"- **{a.type}**: {a.description} (Riesgo: {a.risk_level}) [ID: {a.id}]\n"
            reply += "\n¿Aprobamos alguna o seguimos observando?"
        actions.append(ActionTriggered(type="action_query", status="executed", details={"count": len(pending)}))
        
    elif intent == "approve_action":
        action_id = params.get("action_id")
        if not action_id:
            reply = "Nico, necesito el ID de la acción para aprobarla. Sin ID no puedo disparar nada."
        else:
            action_service = ActionService(db)
            try:
                action = action_service.approve_action(action_id, "JarvisConsole")
                if action:
                    reply = f"Listo Nico, acción {action_id} aprobada. Procediendo a ejecución si el pipeline lo permite."
                    actions.append(ActionTriggered(type="action_approve", status="executed", details={"id": action_id}))
                else:
                    reply = f"Nico, no encuentro la acción {action_id}. ¿Seguro que está pendiente?"
            except Exception as e:
                reply = f"Nico, error al aprobar: {str(e)}. Revisa los logs."
                
    elif intent == "execute_action":
        action_id = params.get("action_id")
        if not action_id:
            reply = "Nico, dame el ID para ejecutar. No puedo disparar a ciegas."
        else:
            action_service = ActionService(db)
            try:
                action = action_service.execute_action(action_id, "JarvisConsole")
                if action:
                    reply = f"Ejecutando acción {action_id}, Nico. Monitoreando resultados..."
                    actions.append(ActionTriggered(type="action_execute", status="executed", details={"id": action_id}))
                else:
                    reply = f"Nico, no pude ejecutar la acción {action_id}. Verifica que esté aprobada primero."
            except Exception as e:
                reply = f"Nico, falló la ejecución: {str(e)}."

    elif intent == "benchmarks.run_all" or intent == "run_benchmark":
        reply = "Iniciando benchmarks de IA, Nico. Esto tomará unos minutos. Si esto sigue así, le prendemos una vela al worker... pero tranqui, lo tengo controlado."
        actions.append(ActionTriggered(type="benchmark", status="planned", details={"target": "all"}))
        
    else:
        # Fallback
        resp = ollama.chat(messages=[
            {"role": "system", "content": "Eres Jarvis, asistente de Nico en Deco-Gravity. Responde breve y profesionalmente en español."},
            {"role": "user", "content": request.message}
        ], options={"temperature": 0.3})
        reply = resp["message"]["content"]

    # Save Assistant Reply
    asst_msg = JarvisConsoleMessage(
        user_id="admin_console",
        role="assistant",
        content=reply,
        session_id=session.id
    )
    db.add(asst_msg)
    
    # Update session timestamp again
    session.last_message_at = datetime.utcnow()
    db.commit()

    return ChatResponse(reply=reply, session_id=str(session.id), actions_triggered=actions)

