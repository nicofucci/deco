from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

VULN_SERVICE_URL = os.getenv("VULN_SERVICE_URL", "http://vuln_service:8083")

from app.models.orchestrator import JarvisScanReport
from app.database import get_db, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends

class ScanRequest(BaseModel):
    target: str
    asset_id: str
    client_id: str = None
    profile: str = "nuclei_basic"

@router.post("/scan")
async def trigger_scan(request: ScanRequest, db: Session = Depends(get_db)):
    """
    Triggers a real scan via Vuln Service.
    """
    logger.info(f"Requesting scan for {request.target} (Asset: {request.asset_id}, Client: {request.client_id})")
    
    async with httpx.AsyncClient() as client:
        try:
            # Call Vuln Service
            payload = {
                "target": request.target,
                "profile": request.profile
            }
            resp = await client.post(f"{VULN_SERVICE_URL}/vuln/scan", json=payload, timeout=10.0)
            
            if resp.status_code != 200:
                logger.error(f"Vuln Service error: {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail="Failed to trigger scan in Vuln Service")
            
            data = resp.json()
            scan_id = data.get("scan_id")
            
            # Create initial ScanReport record to track context
            report = JarvisScanReport(
                scan_id=scan_id,
                asset_id=request.asset_id,
                client_id=request.client_id,
                resumen_tecnico="Escaneo en progreso...",
                riesgos_principales={},
                recomendaciones={}
            )
            db.add(report)
            db.commit()
            
            return {
                "status": "started",
                "scan_id": scan_id,
                "target": request.target,
                "message": "Scan initiated successfully"
            }
            
        except httpx.RequestError as e:
            logger.error(f"Connection error to Vuln Service: {e}")
            raise HTTPException(status_code=503, detail="Vuln Service unavailable")
            raise HTTPException(status_code=503, detail="Vuln Service unavailable")

import subprocess
import uuid
from datetime import datetime

from typing import Optional

class RealScanRequest(BaseModel):
    target: str
    asset_id: Optional[str] = None
    client_id: Optional[str] = None
    ports: str = "top-100" # top-100, full, or specific list

async def run_nmap_scan(scan_id: str, target: str, ports: str, asset_id: Optional[str], client_id: Optional[str]):
    db = SessionLocal()
    try:
        logger.info(f"Starting Nmap scan {scan_id} for {target}...")
        
        # Construct Nmap command
        cmd = ["nmap", "-T4", "-oX", f"/opt/deco/reports/scan_{scan_id}.xml", target]
        if ports == "full":
            cmd.append("-p-")
        elif ports == "top-100":
            cmd.extend(["--top-ports", "100"])
        else:
            cmd.extend(["-p", ports])
            
        # Run scan
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode == 0:
            logger.info(f"Nmap scan {scan_id} completed successfully.")
            status = "completed"
            output = process.stdout
        else:
            logger.error(f"Nmap scan {scan_id} failed: {process.stderr}")
            status = "failed"
            output = process.stderr
            
        # Update Report
        # Note: We should ideally update the existing report created in the endpoint
        # But for simplicity we just log or create a new entry if needed.
        # Here we assume the report was created in the endpoint.
        
        # Parse XML (simplified) or just save raw output
        # For this phase, we just save the status.
        
        # We can use RiskService to update risk based on open ports if we parse XML.
        # For now, let's just mark it done.
        
    except Exception as e:
        logger.error(f"Error in Nmap background task: {e}")
    finally:
        db.close()

@router.post("/scan-real")
async def trigger_real_scan(request: RealScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Executes a REAL Nmap scan from the Jarvis container.
    """
    scan_id = str(uuid.uuid4())
    
    # Create Report Record
    report = JarvisScanReport(
        scan_id=scan_id,
        asset_id=request.asset_id,
        client_id=request.client_id,
        resumen_tecnico=f"Escaneo Nmap Real iniciado para {request.target} ({request.ports})",
        riesgos_principales={},
        recomendaciones={}
    )
    db.add(report)
    db.commit()
    
    # Start Background Task
    background_tasks.add_task(run_nmap_scan, scan_id, request.target, request.ports, request.asset_id, request.client_id)
    
    return {
        "status": "started",
        "scan_id": scan_id,
        "message": "Real Nmap scan started in background"
    }
