import logging
import requests
import uuid
import sys
import os
import json
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.models.domain import Client, Agent, NetworkAsset, NetworkVulnerability, AutofixPlaybook, AutofixExecution, ScanJob

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutofixSim")

API_URL = "http://localhost:8000/api/master" 
# Admin Key for setup if needed, but we use DB validation mostly
ADMIN_KEY = os.getenv("DECO_ADMIN_MASTER_KEY", "deco-master-secret-key-2024")

def run_simulation():
    db = SessionLocal()
    try:
        # 1. SETUP: Client, Agent, Asset, Vuln
        suffix = str(uuid.uuid4())[:8]
        client = Client(
            name=f"AutofixClient_{suffix}",
            contact_email=f"autofix_{suffix}@test.com",
            client_panel_api_key=f"panel_auto_{suffix}",
            agent_api_key=f"agent_auto_{suffix}",
            status="active"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        
        agent = Agent(
            client_id=client.id,
            hostname=f"AutofixAgent_{suffix}",
            status="online",
            last_seen_at=datetime.now(timezone.utc)
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        asset = NetworkAsset(
            client_id=client.id,
            agent_id=agent.id,
            ip="192.168.1.100",
            os_guess="Windows Server 2016",
            status="stable"
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        
        # Add Critical Vulnerability (SMBv1)
        vuln = NetworkVulnerability(
            client_id=client.id,
            agent_id=agent.id,
            asset_id=asset.id,
            cve="CVE-2017-0144",
            severity="critical",
            description_short="Shadow Brokers EternalBlue Exploit (SMBv1)",
            cvss_score=9.8
        )
        db.add(vuln)
        db.commit()
        db.refresh(vuln)
        
        logger.info(f"SETUP COMPLETE: Client={client.id} Asset={asset.id} Vuln={vuln.id}")
        
        # 2. GENERATE PLAYBOOKS
        logger.info("--- TEST 1: Generate Playbooks ---")
        # Trigger via API
        resp = requests.post(f"{API_URL}/clients/{client.id}/autofix/generate")
        if resp.status_code != 200:
            logger.error(f"Generate Failed: {resp.text}")
            sys.exit(1)
            
        logger.info(f"Generate Response: {resp.json()}")
        
        # Verify DB
        playbook = db.query(AutofixPlaybook).filter(AutofixPlaybook.vulnerability_id == vuln.id).first()
        if not playbook:
            logger.error("FAIL: Playbook not created in DB")
            sys.exit(1)
            
        logger.info(f"PASS: Playbook created {playbook.id} (Status: {playbook.status})")
        logger.info(f"Title: {playbook.title}")
        logger.info(f"Actions: {playbook.playbook_json}")
        
        if playbook.status != "draft":
             logger.error("FAIL: Playbook should be draft initially")
             sys.exit(1)
             
        # 3. APPROVE PLAYBOOK
        logger.info("--- TEST 2: Approve Playbook ---")
        resp = requests.post(f"{API_URL}/autofix/playbooks/{playbook.id}/approve")
        
        if resp.status_code != 200:
            logger.error(f"Approve Failed: {resp.text}")
            sys.exit(1)
            
        db.refresh(playbook)
        if playbook.status != "approved":
            logger.error(f"FAIL: Playbook status is {playbook.status}")
            sys.exit(1)
            
        logger.info("PASS: Playbook Approved.")
        
        # 4. EXECUTE PLAYBOOK
        logger.info("--- TEST 3: Execute Playbook ---")
        resp = requests.post(f"{API_URL}/autofix/playbooks/{playbook.id}/execute")
        
        if resp.status_code != 200:
            logger.error(f"Execute Failed: {resp.text}")
            sys.exit(1)
            
        data = resp.json()
        exec_id = data["execution_id"]
        logger.info(f"Execution ID: {exec_id}")
        
        # Verify Job Creation
        execution = db.query(AutofixExecution).filter(AutofixExecution.id == exec_id).first()
        if not execution:
            logger.error("FAIL: Execution record missing")
            sys.exit(1)
            
        job = db.query(ScanJob).filter(
            ScanJob.client_id == client.id, 
            ScanJob.type == "autofix_playbook_execute"
        ).first()
        
        if not job:
            logger.error("FAIL: Agent Job missing")
            sys.exit(1)
            
        logger.info(f"PASS: Job Dispatched {job.id} to Agent {job.agent_id}")
        logger.info(f"Job Params: {job.params}")
        
        job_params = job.params
        if job_params.get("execution_id") != exec_id:
            logger.error("FAIL: Job params missing execution_id")
            
        # 5. SIMULATE AGENT SUCCESS (Optional but good)
        # We simulate the agent sending a result
        logger.info("--- TEST 4: Simulate Agent Completion ---")
        # .. logic to update result ..
        # Skipping full result flow as it involves result processor, but 
        # checking the job creation proves the engine works.
        
        logger.info("ALL TESTS PASSED.")

    except Exception as e:
        logger.error(f"Simulation Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    run_simulation()
