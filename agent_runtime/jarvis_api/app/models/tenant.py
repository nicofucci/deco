from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

from enum import Enum

class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique Tenant ID")
    name: str = Field(..., description="Company Name")
    slug: str = Field(..., description="URL-friendly identifier")
    contact_email: Optional[str] = None
    status: str = Field(default="active") # Simplified enum
    created_at: datetime = Field(default_factory=datetime.now)
    scope_whitelist: List[str] = Field(default_factory=list, description="Allowed IPs/Domains")

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    description: Optional[str] = None
