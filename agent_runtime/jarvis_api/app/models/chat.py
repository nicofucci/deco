from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    auto_title_generated = Column(Boolean, default=False)
    web_search_enabled = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSONB, default=dict)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String, nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    attachments = Column(JSONB, default=list)
    tool_calls = Column(JSONB, default=list)
    uses_web_search = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    embedding = Column(JSONB, nullable=True)
    rag_status = Column(String, default="none")  # none, indexed, ignored
    metadata_ = Column("metadata", JSON, default=dict)

    conversation = relationship("Conversation", back_populates="messages")
