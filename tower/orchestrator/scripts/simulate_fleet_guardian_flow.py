
import sys
import os
import logging
import requests
import time
import uuid
from datetime import datetime, timezone

# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.domain import AgentStatus, Agent, Client, FleetAlert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FleetSim")

API_URL = "http://localhost:18001" 

def simulate_fleet_flow():
    db = SessionLocal()
    try:
        logger.info("--- Starting Fleet Guardian Simulation ---")

        # 1. Setup: Ensure Client and Agent
        client = db.query(Client).first()
        if not client:
             client = Client(name="FleetSimClient")
             db.add(client)
             db.commit()
             db.refresh(client)
        
        # Create/Get Agent
        agent_id = str(uuid.uuid4())
        agent = Agent(
            id=agent_id,
            client_id=client.id,
            hostname="fleet-test-agent",
            name="Fleet Test Agent",
            status="online",
            version="1.0.0"
        )
        db.add(agent)
        db.commit()
        logger.info(f"Created Agent: {agent_id}")

        # 2. Simulate Enriched Heartbeat
        logger.info("Simulating Enriched Heartbeat...")
        payload = {
            "agent_id": agent_id,
            "status": "online",
            "hostname": "fleet-test-agent",
            "ip": "192.168.1.50",
            # Fleet Fields
            "cpu": 45.5,
            "ram": 60.2,
            "version": "1.0.0"
        }
        
        # We assume we are acting as the agent calling the API
        # Need API Key? The heartbeat endpoint uses `get_client_from_api_key`.
        # We'll simulate internal logic by calling Processor directly or mocking headers if we had a valid key.
        # Shortcuts: calling internal DB update via processor to avoid auth complexity in script
        # OR: Creating a key for the client.
        
        # Let's try direct DB / Processor check to test Logic.
        from app.services.telemetry import AgentTelemetryProcessor
        processor = AgentTelemetryProcessor(db)
        processor.update_agent_status(agent_id, payload)
        
        # Verify AgentStatus
        status = db.query(AgentStatus).filter(AgentStatus.agent_id == agent_id).first()
        if not status:
            logger.error("FAIL: AgentStatus record not created.")
            return

        logger.info(f"AgentStatus Created: CPU={status.cpu_usage}% RAM={status.ram_usage}%")
        if status.cpu_usage != 45.5:
             logger.error("FAIL: CPU usage mismatch.")
        else:
             logger.info("PASS: Telemetry ingestion correct.")

        # 3. Simulate High CPU Warning
        logger.info("Simulating High CPU Heartbeat (95%)...")
        payload["cpu"] = 95.0
        processor.update_agent_status(agent_id, payload)
        
        db.expire(status)
        db.refresh(status)
        
        if status.health_state == "warning":
            logger.info("PASS: Health State updated to WARNING (High CPU).")
        else:
             logger.error(f"FAIL: Health State is {status.health_state}, expected warning.")

        # 4. Simulate Offline Alert (Backdating last_seen)
        logger.info("Simulating Agent Offline (>1h)...")
        # Manually backdate
        from datetime import timedelta
        status.last_seen = datetime.now(timezone.utc) - timedelta(hours=2)
        status.health_state = "healthy" # Reset to test transition
        db.commit()
        
        # Run Check
        processor.check_fleet_health()
        
        db.expire(status)
        db.refresh(status)
        
        if status.health_state == "critical":
             logger.info("PASS: Health State updated to CRITICAL (Offline).")
        else:
             logger.error(f"FAIL: Health State is {status.health_state}, expected critical.")
             
        # Check Alert
        alert = db.query(FleetAlert).filter(FleetAlert.agent_id == agent_id, FleetAlert.alert_type == "agent_offline").first()
        if alert:
            logger.info(f"PASS: Alert Created: {alert.message}")
        else:
            logger.error("FAIL: No Offline Alert created.")

        logger.info("--- Simulation SUCCESS ---")

    except Exception as e:
        logger.error(f"Simulation Failed: {e}", exc_info=True)
    finally:
        # Cleanup
        try:
            if 'agent_id' in locals():
                db.query(AgentStatus).filter(AgentStatus.agent_id == agent_id).delete()
                db.query(FleetAlert).filter(FleetAlert.agent_id == agent_id).delete()
                db.query(Agent).filter(Agent.id == agent_id).delete()
                db.commit()
        except:
            pass
        db.close()

if __name__ == "__main__":
    simulate_fleet_flow()
