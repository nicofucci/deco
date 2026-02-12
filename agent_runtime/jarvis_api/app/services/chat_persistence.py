from datetime import datetime
from typing import List, Optional, Dict, Callable

from sqlalchemy.orm import Session

from app.models.chat import Conversation, Message


class ChatPersistenceService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(
        self,
        user_id: str,
        title: str = "Nuevo Chat",
        web_search_enabled: bool = False,
        metadata: Optional[Dict] = None,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            web_search_enabled=web_search_enabled,
            metadata_=metadata or {},
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id, Conversation.is_archived.is_(False))
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )

    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )

    def get_messages(
        self, conversation_id: str, user_id: str, limit: int = 200
    ) -> List[Message]:
        return (
            self.db.query(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        attachments: Optional[List] = None,
        tool_calls: Optional[List] = None,
        uses_web_search: bool = False,
        is_important: bool = False,
        embedder: Optional[Callable[[str], List[float]]] = None,
    ) -> Message:
        embedding = None
        if is_important and embedder:
            try:
                embedding = embedder(content)
            except Exception:
                embedding = None

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            attachments=attachments or [],
            tool_calls=tool_calls or [],
            uses_web_search=uses_web_search,
            is_important=is_important,
            embedding=embedding,
        )
        self.db.add(message)

        conversation = (
            self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        )
        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    def update_conversation_title(
        self, conversation_id: str, title: str, auto_generated: bool = False
    ) -> Optional[Conversation]:
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.title = title
            if auto_generated:
                conversation.auto_title_generated = True
            self.db.commit()
            self.db.refresh(conversation)
            return conversation
        return None

    def update_conversation_settings(
        self, conversation_id: str, user_id: str, web_search_enabled: Optional[bool] = None, title: Optional[str] = None
    ) -> Optional[Conversation]:
        conversation = self.get_conversation(conversation_id=conversation_id, user_id=user_id)
        if not conversation:
            return None

        if web_search_enabled is not None:
            conversation.web_search_enabled = web_search_enabled
        if title is not None:
            conversation.title = title
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        conversation = self.get_conversation(conversation_id=conversation_id, user_id=user_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False
