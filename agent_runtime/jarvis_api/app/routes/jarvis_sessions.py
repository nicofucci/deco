from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.jarvis_console import JarvisSession, JarvisConsoleMessage
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

class SessionCreate(BaseModel):
    title: Optional[str] = None
    user_id: str = "admin_console"

class SessionResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    created_at: datetime
    last_message_at: Optional[datetime]
    is_active: bool

class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime

class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageResponse]

@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    user_id: str = "admin_console", 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    sessions = db.query(JarvisSession)\
        .filter(JarvisSession.user_id == user_id, JarvisSession.is_active == True)\
        .order_by(desc(JarvisSession.last_message_at))\
        .limit(limit)\
        .all()
    return sessions

@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate, db: Session = Depends(get_db)):
    new_session = JarvisSession(
        user_id=request.user_id,
        title=request.title or "Nueva sesión",
        last_message_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def get_session_history(session_id: str, db: Session = Depends(get_db)):
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    session = db.query(JarvisSession).filter(JarvisSession.id == sess_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(JarvisConsoleMessage)\
        .filter(JarvisConsoleMessage.session_id == sess_uuid)\
        .order_by(JarvisConsoleMessage.created_at)\
        .all()
    
    return {
        "session_id": str(session.id),
        "messages": messages
    }

@router.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str, db: Session = Depends(get_db)):
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    session = db.query(JarvisSession).filter(JarvisSession.id == sess_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete messages
    db.query(JarvisConsoleMessage).filter(JarvisConsoleMessage.session_id == sess_uuid).delete()
    db.commit()
    
    return {"status": "cleared"}
