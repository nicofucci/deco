from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.chat import Base

class JarvisSession(Base):
    __tablename__ = "jarvis_console_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(64), index=True, nullable=False, default="admin_console")
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("JarvisConsoleMessage", back_populates="session", cascade="all, delete-orphan")

class JarvisConsoleMessage(Base):
    __tablename__ = "jarvis_console_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("jarvis_console_sessions.id"), nullable=True) # Nullable for migration
    user_id = Column(String(64), index=True, nullable=False, default="admin_console")
    role = Column(String(16), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    session = relationship("JarvisSession", back_populates="messages")

