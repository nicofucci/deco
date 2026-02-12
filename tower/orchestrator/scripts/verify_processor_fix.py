
import sys
import os
import logging
import json
import uuid
from datetime import datetime, timezone

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.domain import Client, ScanJob, ScanResult, NetworkAsset, Agent
from app.services.processor import _process_xray_scan
from sqlalchemy import desc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("XRAY_Sim")

def verify_fix():
    db = SessionLocal()
    try:
        logger.info("--- Starting X-RAY Fix Verification ---")
        
        # 1. Get Client
        client = db.query(Client).filter(Client.name.ilike("%iMac%")).first()
        if not client:
            client = db.query(Client).first()
            logger.warning(f"Fallback client: {client.name}")

        # 2. Mock Agent
        agent = db.query(Agent).filter(Agent.client_id == client.id).first()
        if not agent:
            agent = Agent(client_id=client.id, hostname="mock-agent", ip="192.168.1.50")
            db.add(agent)
            db.commit()
            
        # 3. Create Mock X-RAY Job
        job = ScanJob(
            client_id=client.id,
            agent_id=agent.id,
            type="xray_network_scan",
            status="done",
            target="192.168.1.0/24",
            finished_at=datetime.now(timezone.utc)
        )
        db.add(job)
        db.commit()
        logger.info(f"Created Mock Job: {job.id}")
        
        # 4. Create Simulated "Success" Result (as if new agent sent it)
        simulated_data = {
            "target": "192.168.1.0/24",
            "devices": [
                {
                    "ip": "192.168.1.101", 
                    "hostname": "Printer-HP", 
                    "status": "active",
                    "device_type": "printer",
                    "open_ports": [80, 515, 631],
                    "os_guess": "Embedded Linux"
                },
                {
                    "ip": "192.168.1.102", 
                    "hostname": "CEO-Laptop", 
                    "status": "active", 
                    "device_type": "pc",
                    "open_ports": [135, 139, 445], 
                    "os_guess": "Windows 11"
                }
            ],
            "count": 2
        }
        
        # 5. Process directly using the fixed function
        logger.info("Processing simulated result with _process_xray_scan...")
        _process_xray_scan(db, job, agent, simulated_data)
        
        # 6. Verify Database
        assets = db.query(NetworkAsset).filter(NetworkAsset.client_id == client.id).all()
        logger.info(f"Total Network Assets: {len(assets)}")
        
        found_printer = False
        found_pc = False
        
        for asset in assets:
            if asset.ip == "192.168.1.101" and asset.device_type == "printer":
                found_printer = True
                logger.info("SUCCESS: Printer found in DB")
            if asset.ip == "192.168.1.102" and asset.device_type == "pc":
                found_pc = True
                logger.info("SUCCESS: PC found in DB")
                
        if found_printer and found_pc:
            logger.info("VERIFICATION PASSED: assets stored correctly.")
        else:
            logger.error("VERIFICATION FAILED: assets missing.")

    except Exception as e:
        logger.error(f"Verification Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    verify_fix()
