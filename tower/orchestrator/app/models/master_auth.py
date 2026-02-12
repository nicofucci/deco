from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class MasterAdmin(Base):
    __tablename__ = "master_admin"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False) # Fixed to "Deco"
    password_hash = Column(String, nullable=False) # For bootstrap
    webauthn_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    credentials = relationship("MasterWebAuthnCredential", back_populates="admin")

class MasterWebAuthnCredential(Base):
    __tablename__ = "master_webauthn_credentials"

    id = Column(String, primary_key=True, default=generate_uuid)
    admin_id = Column(String, ForeignKey("master_admin.id"), nullable=False)
    credential_id = Column(String, nullable=False) # Base64 encoded usually
    public_key = Column(String, nullable=False) # Base64 encoded
    sign_count = Column(Integer, default=0)
    label = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    admin = relationship("MasterAdmin", back_populates="credentials")
