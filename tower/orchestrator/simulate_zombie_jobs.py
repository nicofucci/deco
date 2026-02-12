import logging
import requests
import uuid
import time
import sys
import os
from datetime import datetime, timezone
import json

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZombieSim")

API_URL = "http://localhost:18001/api/master" # We simulate external access internally or direct
# Actually simulating from inside the container or host?
# If running via docker exec orchestrator_api, we use localhost:8000
# But I will run this script likely from inside orchestrator container for easy DB access if needed, 
# or just use request to localhost:8000 (which is Main API).
# Wait, Orchestrator runs on 8000 inside container.
API_BASE = "http://localhost:8000/api"

# Admin Key for setup
ADMIN_KEY = os.getenv("DECO_ADMIN_MASTER_KEY", "deco-master-secret-key-2024")

def setup_client_and_agent():
    # 1. Create Client
    suffix = str(uuid.uuid4())[:8]
    client_payload = {
        "name": f"ZombieTestClient_{suffix}",
        "contact_email": f"zombie_{suffix}@test.com"
    }
    headers = {"X-Admin-Master-Key": ADMIN_KEY}
    
    # We need to use valid endpoints. 
    # Create Client via Partner/Admin API? Or just use existing if problematic.
    # We'll use a known trick: Insert directly to DB or use correct endpoint.
    # Let's try to use the Partner API flow or Master API if available.
    # Since I am in orchestrator, I can import models and insert directly to avoid API chaos for test setup.
    pass

# We will use direct DB manipulation for setup to guarantee clean state
from app.db.session import SessionLocal
from app.models.domain import Client, Agent, ScanJob

def run_simulation():
    db = SessionLocal()
    try:
        # SETUP
        suffix = str(uuid.uuid4())[:8]
        client = Client(
            name=f"ZombieClient_{suffix}",
            contact_email=f"zombie_{suffix}@test.com",
            client_panel_api_key=f"panel_{suffix}",
            agent_api_key=f"agent_{suffix}",
            status="active"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        
        agent = Agent(
            client_id=client.id,
            hostname=f"ZombieAgent_{suffix}",
            status="online",
            last_seen_at=datetime.now(timezone.utc)
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        logger.info(f"SETUP: Created Client {client.id} and Agent {agent.id}")
        
        # SCENARIO 1: FETCH BUT NO ACK (Simulating Crash before Start)
        logger.info("--- SCENARIO 1: Fetch -> No ACK ---")
        job1 = ScanJob(
            client_id=client.id,
            agent_id=None, # Unassigned initially
            type="xray_network_scan",
            target="192.168.1.1",
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(job1)
        db.commit()
        
        # Agent Fetches Jobs
        # Simulate GET /jobs
        # We need to hit the API to trigger the logic
        requests.get(f"{API_BASE}/agents/ping") # Warmup
        
        headers = {"X-Client-API-Key": client.agent_api_key}
        resp = requests.get(f"{API_BASE}/agents/jobs?agent_id={agent.id}", headers=headers)
        if resp.status_code != 200:
            logger.error(f"Failed to fetch jobs: {resp.text}")
            sys.exit(1)
            
        jobs = resp.json()
        target_job = next((j for j in jobs if j["id"] == job1.id), None)
        
        if not target_job:
            logger.error("Job 1 not found in fetch response")
            sys.exit(1)
            
        logger.info(f"Fetched Job Status: {target_job['status']}")
        
        # Verify in DB it is NOT running
        db.refresh(job1)
        if job1.status == "running":
            logger.error("FAIL: Job 1 became RUNNING immediately after fetch!")
        else:
            logger.info("PASS: Job 1 is NOT RUNNING after fetch (Waiting for ACK).")
            if job1.agent_id == agent.id:
                logger.info("PASS: Job 1 is assigned to agent.")

        # SCENARIO 2: FETCH -> ACK -> TIMEOUT (Zombie)
        logger.info("--- SCENARIO 2: Fetch -> ACK -> Timeout ---")
        job2 = ScanJob(
            client_id=client.id,
            type="xray_network_scan",
            target="192.168.1.2",
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(job2)
        db.commit()
        
        # Fetch
        requests.get(f"{API_BASE}/agents/jobs?agent_id={agent.id}", headers=headers)
        
        # ACK
        ack_resp = requests.post(f"{API_BASE}/agents/jobs/{job2.id}/ack", headers=headers)
        if ack_resp.status_code != 200:
            logger.error(f"ACK Failed: {ack_resp.text}")
        else:
            logger.info("ACK Successful.")
            
        db.refresh(job2)
        if job2.status != "running":
            logger.error(f"FAIL: Job 2 status is {job2.status} after ACK (expected running)")
        else:
            logger.info("PASS: Job 2 became RUNNING after ACK.")
            if not job2.started_at:
                 logger.error("FAIL: Job 2 has NO started_at after ACK")
            else:
                 logger.info("PASS: Job 2 has started_at set.")
                 
        # Simulate Time Travel for Timeout
        logger.info("Simulating 35 minutes passage...")
        # Since we can't easily change system time, we will manually update the job in DB
        # to look old
        from datetime import timedelta
        old_time = datetime.now(timezone.utc) - timedelta(minutes=40)
        job2.started_at = old_time
        db.commit()
        
        # Trigger Cleaner
        logger.info("Triggering Zombie Cleaner...")
        # We can call the function directly by importing it, or wait for scheduler.
        # Calling directly for speed.
        sys.path.append("/app")
        from app.services.scheduler import check_zombie_jobs
        check_zombie_jobs()
        
        db.refresh(job2)
        logger.info(f"Job 2 Status after Cleaner: {job2.status}")
        
        if job2.status == "error":
            logger.info("PASS: Job 2 was killed by Zombie Cleaner.")
            logger.info(f"Error Reason: {job2.params.get('error_reason')}")
        else:
            logger.error(f"FAIL: Job 2 is still {job2.status}")

    except Exception as e:
        logger.error(f"Simulation Failed: {e}", exc_info=True)
    finally:
        # Cleanup
        # db.delete(client) # Cascade?
        db.close()

if __name__ == "__main__":
    run_simulation()
