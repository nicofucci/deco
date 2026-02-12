from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.chat import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class CaseORM(Base):
    __tablename__ = "cases"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="open") # open, closed, in_progress
    severity = Column(String, default="medium") # low, medium, high, critical
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)
