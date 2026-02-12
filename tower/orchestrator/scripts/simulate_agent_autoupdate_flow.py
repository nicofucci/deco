
import sys
import os
import logging
import uuid
import requests
import json
from datetime import datetime, timezone

# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.domain import AgentVersion, Agent, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoUpdateSim")

API_URL = "http://localhost:18001" 

def simulate_flow():
    db = SessionLocal()
    try:
        logger.info("--- Starting Auto-Update Simulation ---")

        # 1. Setup: Create AgentVersion 1.1.0 in DB
        version_1_1 = AgentVersion(
            version="1.1.0",
            platform="windows",
            download_url="https://download.deco-security.com/v1.1.0/DecoAgent-Windows.exe", # Mock
            checksum_sha256="mock_sha256_hash_12345",
            is_forced=False,
            changelog="Simulated Update 1.1.0"
        )
        # Check if exists
        existing = db.query(AgentVersion).filter_by(version="1.1.0").first()
        if not existing:
            db.add(version_1_1)
            db.commit()
            logger.info("Created AgentVersion 1.1.0 in DB.")
        else:
            logger.info("AgentVersion 1.1.0 already exists.")

        # 2. Setup: Ensure a Client and Agent exist
        client = db.query(Client).first()
        if not client:
             client = Client(name="UpdateSimClient")
             db.add(client)
             db.commit()
        
        agent = db.query(Agent).filter(Agent.client_id == client.id).first()
        if not agent:
            agent = Agent(client_id=client.id, hostname="update-test-agent", ip="10.0.0.99", version="1.0.0")
            db.add(agent)
            db.commit()
        
        agent_id = agent.id
        logger.info(f"Using Agent: {agent_id} (Current Ver: {agent.version})")

        # 3. Simulate Agent Check (GET /update-metadata)
        logger.info("Simulating Agent Check (GET /update-metadata)...")
        resp = requests.get(f"{API_URL}/api/agents/update-metadata", params={
            "platform": "windows",
            "current_version": "1.0.0",
            "agent_id": agent_id
        })
        
        data = resp.json()
        logger.info(f"Metadata Response: {data}")
        
        if not data.get("update_available"):
            logger.error("FAIL: Expected update_available=True")
            return

        if data.get("latest_version") != "1.1.0":
            logger.error(f"FAIL: Expected 1.1.0, got {data.get('latest_version')}")
            return

        logger.info("PASS: Update metadata correct.")

        # 4. Simulate Agent Status Report (POST /update-status)
        logger.info("Simulating Agent Status Report (POST /update-status)...")
        payload = {
            "previous_version": "1.0.0",
            "new_version": "1.1.0",
            "status": "success",
            "message": "Simulation Success"
        }
        
        resp = requests.post(f"{API_URL}/api/agents/{agent_id}/update-status", json=payload)
        logger.info(f"Status Report Response: {resp.status_code}")
        
        if resp.status_code != 200:
             logger.error("FAIL: API rejected status report.")
             return

        # 5. Verify DB Update
        db.expire(agent)
        db.refresh(agent)
        logger.info(f"Agent Version in DB after update: {agent.version}")
        
        if agent.version == "1.1.0":
            logger.info("PASS: Agent version updated in DB.")
            logger.info("--- Simulation SUCCESS ---")
        else:
            logger.error("FAIL: Agent version NOT updated in DB.")

    except Exception as e:
        logger.error(f"Simulation Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    simulate_flow()
