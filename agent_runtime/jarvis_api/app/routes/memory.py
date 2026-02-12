from fastapi import APIRouter, Depends
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
from app.dependencies import get_current_user

router = APIRouter()

class MemoryItem(BaseModel):
    id: str
    title: str
    category: str
    confidence: float
    timestamp: datetime
    summary: str

# Mock Data for now - In future connect to Qdrant
MOCK_MEMORY = [
    MemoryItem(
        id="mem_001",
        title="Network Topology - 192.168.1.0/24",
        category="Reconnaissance",
        confidence=0.95,
        timestamp=datetime.now(),
        summary="Detected 5 active hosts. Gateway at .1. Kali Node at .55."
    ),
    MemoryItem(
        id="mem_002",
        title="CVE-2023-44487 - HTTP/2 Rapid Reset",
        category="Vulnerability",
        confidence=0.98,
        timestamp=datetime.now(),
        summary="Critical vulnerability affecting HTTP/2 protocol. Mitigation required on Nginx ingress."
    ),
    MemoryItem(
        id="mem_003",
        title="SSH Hardening Policy",
        category="Configuration",
        confidence=0.85,
        timestamp=datetime.now(),
        summary="Root login disabled. Key-based auth enforced. Port 22 open."
    ),
    MemoryItem(
        id="mem_004",
        title="Target A - Web Server",
        category="Asset",
        confidence=0.90,
        timestamp=datetime.now(),
        summary="Apache 2.4.50 running on Ubuntu 20.04. Potential path traversal vulnerability."
    )
]

@router.get("/items", response_model=List[MemoryItem])
async def list_memory_items(user: Dict = Depends(get_current_user)):
    """Lista los items de conocimiento almacenados en la memoria a largo plazo (RAG)."""
    return MOCK_MEMORY
