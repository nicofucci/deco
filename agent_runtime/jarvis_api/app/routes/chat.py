from datetime import datetime
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.jarvis_prime.orchestrator import jarvis_prime
from app.services.chat_persistence import ChatPersistenceService
from app.services.ollama_client import JarvisOllamaClient

router = APIRouter()

ollama_client = JarvisOllamaClient()


class MessageSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    uses_web_search: bool = False
    is_important: bool = False

    class Config:
        from_attributes = True


class ConversationSchema(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    auto_title_generated: bool = False
    web_search_enabled: bool = False
    messages: List[MessageSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConversationSummarySchema(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    auto_title_generated: bool = False
    web_search_enabled: bool = False

    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "Nuevo Chat"
    web_search_enabled: bool = False


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None
    web_search_enabled: Optional[bool] = None


class ChatMessageRequest(BaseModel):
    message: str
    use_web_search: bool = False
    is_important: bool = False
    attachments: List[Dict[str, Any]] = Field(default_factory=list)


async def get_chat_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
):
    """Intenta autenticar; si falla, usa perfil invitado para permitir chat sin login."""
    if credentials:
        try:
            from app.dependencies import auth_system

            payload = auth_system.verify_token(credentials.credentials, "access")
            if payload:
                return payload
        except Exception:
            pass

    return {"sub": "guest", "username": "guest", "role": "viewer"}


def _serialize_message(message) -> Dict[str, Any]:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
        "attachments": message.attachments or [],
        "uses_web_search": message.uses_web_search,
        "is_important": getattr(message, "is_important", False),
    }


def _should_generate_title(messages: List[Any]) -> bool:
    user_messages = [m for m in messages if m.role == "user"]
    return len(user_messages) >= 2


def _maybe_generate_auto_title(
    service: ChatPersistenceService,
    conversation,
    messages: List[Any],
):
    """Genera título corto en el segundo turno usando un modelo ligero."""
    if not conversation or conversation.auto_title_generated:
        return

    if not _should_generate_title(messages):
        return

    try:
        context_snippet = "\n".join([f"- {m.role}: {m.content[:140]}" for m in messages[-4:]])
        prompt = [
            {
                "role": "system",
                "content": "Genera un título corto (máx 8 palabras) para esta conversación de ciberseguridad en español.",
            },
            {"role": "user", "content": context_snippet},
        ]
        resp = ollama_client.chat(messages=prompt, model="llama3.1:8b-instruct-q4_K_M")
        candidate = resp.get("message", {}).get("content", "").split("\n")[0].strip()
        if candidate:
            title = candidate[:80]
            service.update_conversation_title(conversation.id, title, auto_generated=True)
    except Exception:
        # Silenciar errores de título para no bloquear el chat
        pass


@router.get("/conversations", response_model=List[ConversationSummarySchema])
async def list_conversations(user: Dict = Depends(get_chat_user), db: Session = Depends(get_db)):
    service = ChatPersistenceService(db)
    conversations = service.get_conversations(user_id=user.get("sub", "guest"))
    return conversations


@router.post("/conversations", response_model=ConversationSchema)
async def create_conversation(
    request: CreateConversationRequest,
    user: Dict = Depends(get_chat_user),
    db: Session = Depends(get_db),
):
    service = ChatPersistenceService(db)
    conversation = service.create_conversation(
        user_id=user.get("sub", "guest"),
        title=request.title,
        web_search_enabled=request.web_search_enabled,
    )
    # Mensaje inicial para UX
    service.save_message(
        conversation_id=conversation.id,
        role="assistant",
        content="Hola, soy Jarvis. ¿En qué puedo ayudarte hoy?",
    )
    db.refresh(conversation)
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(
    conversation_id: str,
    user: Dict = Depends(get_chat_user),
    db: Session = Depends(get_db),
):
    service = ChatPersistenceService(db)
    conversation = service.get_conversation(conversation_id=conversation_id, user_id=user.get("sub", "guest"))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageSchema])
async def get_conversation_messages(
    conversation_id: str,
    user: Dict = Depends(get_chat_user),
    db: Session = Depends(get_db),
):
    service = ChatPersistenceService(db)
    conversation = service.get_conversation(conversation_id=conversation_id, user_id=user.get("sub", "guest"))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    messages = service.get_messages(conversation_id=conversation_id, user_id=user.get("sub", "guest"))
    return messages


@router.patch("/conversations/{conversation_id}", response_model=ConversationSchema)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    user: Dict = Depends(get_chat_user),
    db: Session = Depends(get_db),
):
    service = ChatPersistenceService(db)
    updated = service.update_conversation_settings(
        conversation_id=conversation_id,
        user_id=user.get("sub", "guest"),
        web_search_enabled=request.web_search_enabled,
        title=request.title,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return updated


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: Dict = Depends(get_chat_user),
    db: Session = Depends(get_db),
):
    service = ChatPersistenceService(db)
    deleted = service.delete_conversation(conversation_id=conversation_id, user_id=user.get("sub", "guest"))
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return {"status": "deleted", "id": conversation_id}


@router.post("/conversations/{conversation_id}/message")
async def send_message(
    conversation_id: str,
    request: ChatMessageRequest,
    user: Dict = Depends(get_chat_user),
    db: Session = Depends(get_db),
):
    """Envía un mensaje a una conversación y persiste el historial."""
    service = ChatPersistenceService(db)
    conversation = service.get_conversation(conversation_id=conversation_id, user_id=user.get("sub", "guest"))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # Guardar mensaje de usuario
    user_message = service.save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        attachments=request.attachments,
        uses_web_search=request.use_web_search,
        is_important=request.is_important,
        embedder=ollama_client.generate_embedding if request.is_important else None,
    )

    # Construir historial limpio para Jarvis Prime
    history_records = service.get_messages(conversation_id=conversation_id, user_id=user.get("sub", "guest"))
    history_payload = [{"role": m.role, "content": m.content} for m in history_records]

    context = {
        "user_id": user.get("username", "guest"),
        "conversation_id": conversation_id,
        "use_web_search": request.use_web_search or conversation.web_search_enabled,
    }

    try:
        result = await jarvis_prime.process_user_request(
            user_input=request.message,
            user_id=str(conversation_id),
            context=context,
            history=history_payload,
            use_web_search=context["use_web_search"],
        )
        assistant_content = result.get("message", "No pude generar respuesta.")
    except Exception as exc:
        assistant_content = f"Error procesando solicitud: {exc}"

    assistant_message = service.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_content,
        uses_web_search=context["use_web_search"],
    )

    # Intentar generar título automático en el segundo turno
    _maybe_generate_auto_title(service, conversation, history_records + [assistant_message])

    return {
        "assistant_message": _serialize_message(assistant_message),
        "conversation": conversation,
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user: Dict = Depends(get_chat_user)):
    """Sube un archivo para análisis."""
    try:
        upload_dir = Path("/opt/deco/agent_runtime/data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        file_path = upload_dir / f"{file_id}{file_ext}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "file_id": file_id,
            "filename": file.filename,
            "path": str(file_path),
            "type": file.content_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo archivo: {str(e)}")


class AnalyzeRequest(BaseModel):
    target: str  # URL o File ID
    type: str  # 'url', 'file', 'text'
    instruction: Optional[str] = "Analiza esto"


@router.post("/analyze")
async def analyze_content(request: AnalyzeRequest, user: Dict = Depends(get_chat_user)):
    """Analiza contenido (URL o Archivo) usando agentes."""
    try:
        analysis_result = f"Análisis iniciado para {request.target} ({request.type}).\n\n"

        if request.type == "url":
            analysis_result += (
                f"🔍 **Escaneo de URL detectado**\n- Target: {request.target}\n- Agente: A-SCAN\n- Estado: En cola..."
            )
        elif request.type == "file":
            analysis_result += (
                f"📄 **Análisis de Documento**\n- Archivo: {request.target}\n- Agente: A-RAG\n- Estado: Procesando..."
            )

        return {
            "message": analysis_result,
            "status": "processing",
            "agent": "Jarvis Prime",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")


@router.post("/send")
async def send_simple_message(request: ChatMessageRequest):
    """Endpoint simplificado para testing rápido del chat."""
    try:
        response = ollama_client.chat(
            messages=[
                {
                    "role": "system",
                    "content": "Eres Jarvis, un asistente de ciberseguridad y pentesting. Responde de forma concisa y profesional. IMPORTANTE: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL.",
                },
                {"role": "user", "content": request.message},
            ]
        )

        return {
            "response": response["message"]["content"],
            "model": response.get("model", "llama3.1:8b"),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en chat: {str(e)}")
