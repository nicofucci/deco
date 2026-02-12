"""
Agent Communication Protocol
Defines standard message formats for inter-agent communication
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Status of agent response"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentStatus(str, Enum):
    """Current status of an agent"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    STARTING = "starting"


class AgentMessage(BaseModel):
    """Standard format for messages sent to agents"""
    request_id: str = Field(..., description="Unique request identifier")
    from_agent: str = Field(..., description="Source agent code or 'jarvis-prime'")
    to_agent: str = Field(..., description="Target agent code")
    intent: str = Field(..., description="What is being requested")
    params: Dict[str, Any] = Field(default_factory=dict, description="Request parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Shared context")
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=5, description="Priority 1-10, 10=highest")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentResponse(BaseModel):
    """Standard format for agent responses"""
    request_id: str = Field(..., description="Matches request ID")
    agent_code: str = Field(..., description="Responding agent code")
    status: ResponseStatus = Field(..., description="Response status")
    
    # Human-readable summary for Jarvis
    summary: str = Field(..., description="Natural language summary")
    
    # Structured data
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed results")
    
    # Generated artifacts (files, reports, etc.)
    artifacts: List[str] = Field(default_factory=list, description="Paths to generated files")
    
    # Suggestions for next steps
    next_steps: List[str] = Field(default_factory=list, description="Recommended actions")
    
    # Confidence and errors
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence 0-1")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AuditEntry(BaseModel):
    """Log entry for agent actions"""
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_code: str
    action: str
    triggered_by: str  # user ID or 'jarvis-prime' or other agent
    params: Dict[str, Any] = Field(default_factory=dict)
    result_status: ResponseStatus
    execution_time_ms: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
