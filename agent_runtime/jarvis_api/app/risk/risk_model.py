from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Entity identifiers (nullable depending on what we are scoring)
    client_id = Column(String, nullable=True, index=True)
    asset_id = Column(String, nullable=True, index=True)
    agent_key = Column(String, nullable=True, index=True)
    
    # Risk Metrics
    score_actual = Column(Float, default=0.0) # 0-100
    trend = Column(String, default="flat") # up, down, flat
    
    # Predictions
    risk_24h = Column(Float, default=0.0)
    risk_72h = Column(Float, default=0.0)
    risk_7d = Column(Float, default=0.0)
    
    # Classification
    category = Column(String, default="low") # low, medium, high, critical
    
    # Metadata for context (why is risk high?)
    risk_metadata = Column(JSON, default={}) # "metadata" is reserved in SQLAlchemy Base
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
