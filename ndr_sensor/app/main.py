from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import logging
import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from app.scanner_active import ActiveScanner
from app.scanner_passive import PassiveScanner
from app.orch_client import OrchClient

load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ndr_sensor")

app = FastAPI(title="Deco NDR Sensor", version="0.1")

# Components
active_scanner = ActiveScanner()
passive_scanner = PassiveScanner()
orch_client = OrchClient()
scheduler = AsyncIOScheduler()

# Config
DEFAULT_CIDR = os.getenv("DEFAULT_CIDR", "192.168.100.0/24")
DEFAULT_CLIENT_ID = os.getenv("DEFAULT_CLIENT_ID")

class ActiveScanRequest(BaseModel):
    client_id: str
    cidr: str = DEFAULT_CIDR
    mode: str = "fast" # or full

class PassiveScanRequest(BaseModel):
    client_id: str
    seconds: int = 60

class RunRequest(BaseModel):
    client_id: str
    cidr: str = DEFAULT_CIDR

@app.on_event("startup")
async def startup_event():
    # Start Scheduler
    if DEFAULT_CLIENT_ID:
        scheduler.add_job(scheduled_active_fast, 'interval', minutes=10, args=[DEFAULT_CLIENT_ID, DEFAULT_CIDR])
        scheduler.add_job(scheduled_active_full, 'interval', minutes=60, args=[DEFAULT_CLIENT_ID, DEFAULT_CIDR])
    scheduler.start()
    logger.info("NDR Sensor Started")

@app.get("/health")
def health():
    return {"status": "ok", "ts": os.getenv("NDR_PORT"), "version": "0.1"}

@app.post("/scan/active")
async def scan_active(req: ActiveScanRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_active_scan, req.client_id, req.cidr, req.mode)
    return {"status": "queued", "mode": req.mode}

@app.post("/scan/passive")
async def scan_passive(req: PassiveScanRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_passive_scan, req.client_id, req.seconds)
    return {"status": "queued", "seconds": req.seconds}

@app.post("/scan/run")
async def run_all(req: RunRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_full_run, req.client_id, req.cidr)
    return {"status": "queued", "type": "full_run"}

# Execution Logic
def run_active_scan(client_id: str, cidr: str, mode: str):
    logger.info(f"Starting Active Scan ({mode}) on {cidr}")
    obs = active_scanner.run_scan(cidr, mode)
    if obs:
        orch_client.ingest(client_id, obs)

def run_passive_scan(client_id: str, seconds: int):
    logger.info(f"Starting Passive Scan ({seconds}s)")
    obs = passive_scanner.scan(seconds)
    if obs:
        orch_client.ingest(client_id, obs)

def execute_full_run(client_id: str, cidr: str):
    # Active Fast
    run_active_scan(client_id, cidr, "fast")
    # Passive Short
    run_passive_scan(client_id, 30)

# Scheduled Jobs
def scheduled_active_fast(client_id, cidr):
    run_active_scan(client_id, cidr, "fast")
    
def scheduled_active_full(client_id, cidr):
    run_active_scan(client_id, cidr, "full")
