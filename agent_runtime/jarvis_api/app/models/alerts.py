from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, JSON
from sqlalchemy.sql import func
from app.models.chat import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class SystemAlert(Base):
    __tablename__ = "system_alerts"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=generate_uuid)
    
    # Core fields
    type = Column(String, nullable=False)  # AI_PERFORMANCE, PENTEST, SYSTEM_HEALTH
    severity = Column(String, nullable=False)  # low, medium, high, critical
    status = Column(String, default="open")  # open, acknowledged, resolved
    source = Column(String, nullable=True)  # ai_benchmarks, vuln_service, monitoring
    
    # Content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Context / Relations
    agent_key = Column(String, nullable=True)
    client_id = Column(String, nullable=True) # UUID as string if needed, or just String
    asset_id = Column(String, nullable=True)
    scan_id = Column(String, nullable=True)
    
    # Metrics
    score = Column(Float, nullable=True)
    metric_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    
    # Extra
    alert_metadata = Column("metadata", JSON, nullable=True)
    
    # New Fields Phase 8
    agent_name = Column(String, nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    recommended_action = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "status": self.status,
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "agent_key": self.agent_key,
            "client_id": self.client_id,
            "asset_id": self.asset_id,
            "scan_id": self.scan_id,
            "score": self.score,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "threshold": self.threshold,
            "metadata": self.alert_metadata,
            "agent_name": self.agent_name,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "recommended_action": self.recommended_action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }

Alert = SystemAlert
