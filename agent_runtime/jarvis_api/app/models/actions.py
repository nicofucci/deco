from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class ProposedAction(Base):
    __tablename__ = "proposed_actions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    type = Column(String, index=True) # e.g., "restart_service", "scan_target"
    source_alert_id = Column(String, nullable=True) # Link to alert
    description = Column(String)
    risk_level = Column(String) # low, medium, high, critical
    recommended_by = Column(String) # e.g., "system_health_watcher"
    
    status = Column(String, default="pending", index=True) # pending, approved, rejected, executed
    
    payload = Column(JSON, default={}) # Parameters for execution
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    executed_by = Column(String, nullable=True) # Operator name
