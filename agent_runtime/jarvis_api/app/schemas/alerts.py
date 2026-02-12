from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class AlertBase(BaseModel):
    type: str = Field(..., description="Type of the alert (e.g., AI_PERFORMANCE, PENTEST)")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    source: Optional[str] = Field(None, description="Source of the alert")
    title: str = Field(..., description="Short title of the alert")
    description: Optional[str] = Field(None, description="Detailed description")
    
    agent_key: Optional[str] = None
    client_id: Optional[str] = None
    asset_id: Optional[str] = None
    scan_id: Optional[str] = None
    
    score: Optional[float] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    
    # New Fields Phase 8
    agent_name: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    recommended_action: Optional[str] = None

class AlertCreate(AlertBase):
    metadata: Optional[Dict[str, Any]] = Field(None, description="Extra payload")

class AlertUpdateStatus(BaseModel):
    status: str = Field(..., description="New status: open, acknowledged, resolved")

class AlertRead(AlertBase):
    id: str
    status: str
    alert_metadata: Optional[Dict[str, Any]] = Field(None, serialization_alias="metadata")
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
