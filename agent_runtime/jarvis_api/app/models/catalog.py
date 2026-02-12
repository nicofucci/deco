from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class ActionLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ActionCategory(str, Enum):
    RECON = "recon"
    SCANNING = "scanning"
    EXPLOITATION = "exploitation"
    POST_EXPLOIT = "post-exploit"
    REPORTING = "reporting"
    HARDENING = "hardening"
    OSINT = "osint"

class Action(BaseModel):
    id: str
    code: str
    name: str
    category: ActionCategory
    level: ActionLevel
    risk: str = "low"  # low, medium, high, critical
    requires_otp: bool = False
    script_path_kali: str
    description: Optional[str] = None
    tags: List[str] = []

class ServiceType(str, Enum):
    MANAGED = "managed"
    PENTEST = "pentest"
    DEVSECOPS = "devsecops"
    TRAINING = "training"
    PACKAGE = "package"

class ServiceActionLink(BaseModel):
    action_id: str
    order: int
    role: str  # e.g., "initial_recon", "deep_scan"

class Service(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    type: ServiceType
    level: ActionLevel
    description: str
    tags: List[str] = []
    pipeline: List[ServiceActionLink] = []
    status: Literal["beta", "stable", "lab"] = "lab"
