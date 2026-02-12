from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class NodeType(str, Enum):
    SCANNER = "scanner"
    SENSOR = "sensor"
    RELAY = "relay"

class NodeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

class Node(BaseModel):
    id: str = Field(..., description="Unique Identifier (UUID)")
    name: str = Field(..., description="Friendly name")
    type: NodeType = Field(default=NodeType.SCANNER)
    host: str = Field(..., description="IP or Hostname")
    protocol: str = Field(default="ssh", description="ssh, https, local")
    user: Optional[str] = Field(default="kali", description="SSH User")
    key_path: Optional[str] = Field(None, description="Path to SSH Key")
    status: NodeStatus = Field(default=NodeStatus.OFFLINE)
    last_seen: Optional[datetime] = None
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
