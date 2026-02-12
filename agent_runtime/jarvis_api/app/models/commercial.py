from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class Client(BaseModel):
    id: str = str(uuid.uuid4())
    name: str
    industry: str
    contact_email: str
    status: str = "active"
    created_at: datetime = datetime.now()

class Project(BaseModel):
    id: str = str(uuid.uuid4())
    client_id: str
    name: str
    description: str
    status: str = "active" # active, completed, archived
    start_date: datetime = datetime.now()
    end_date: Optional[datetime] = None

# Mock Database
MOCK_CLIENTS = [
    Client(id="cli_001", name="Acme Corp", industry="Finance", contact_email="security@acme.com"),
    Client(id="cli_002", name="CyberDyne Systems", industry="Defense", contact_email="admin@cyberdyne.net")
]

MOCK_PROJECTS = [
    Project(id="prj_001", client_id="cli_001", name="Q4 Pentest", description="Auditoría trimestral de perímetro."),
    Project(id="prj_002", client_id="cli_002", name="Skynet Hardening", description="Aseguramiento de infraestructura crítica.")
]
