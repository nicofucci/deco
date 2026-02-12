from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Client, Asset, VulnScan, VulnFinding
from typing import List, Optional

router = APIRouter()

async def get_client_by_key(x_client_api_key: str = Header(...), db: AsyncSession = Depends(get_db)):
    # Mock validation for now or implement real key check
    # In V3, we might need to check ActivationCode or Client table if keys are stored there
    # For now, we'll assume any key starting with "client_" is valid and map to first client
    if not x_client_api_key:
        raise HTTPException(status_code=401, detail="API Key missing")
    
    # Mock: Return first client
    result = await db.execute(select(Client))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/findings")
async def get_client_findings(asset_id: Optional[str] = None, client: Client = Depends(get_client_by_key), db: AsyncSession = Depends(get_db)):
    # Return mock findings or query DB
    return [
        {"id": "f1", "severity": "critical", "name": "SQL Injection", "asset": "Web Server", "status": "open"},
        {"id": "f2", "severity": "high", "name": "XSS", "asset": "App Server", "status": "open"}
    ]

@router.get("/assets")
async def get_client_assets(client: Client = Depends(get_client_by_key), db: AsyncSession = Depends(get_db)):
    # Query assets for this client
    # Assuming Asset model has client_id
    # result = await db.execute(select(Asset).where(Asset.client_id == client.id))
    # return result.scalars().all()
    return [
        {"id": "a1", "hostname": "web-server", "ip": "192.168.1.10", "os": "Linux"},
        {"id": "a2", "hostname": "db-server", "ip": "192.168.1.11", "os": "Linux"}
    ]

@router.get("/jobs")
async def get_client_jobs(client: Client = Depends(get_client_by_key)):
    return []

@router.post("/reports/summary")
async def generate_report(client: Client = Depends(get_client_by_key)):
    return {"status": "ok", "url": "http://mock-report-url.pdf"}
