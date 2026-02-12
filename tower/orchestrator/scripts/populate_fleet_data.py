
import sys
import os
import logging
import uuid
from datetime import datetime, timezone

# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.domain import AgentStatus, Agent, Client, FleetAlert
from app.services.telemetry import AgentTelemetryProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FleetPopulate")

def populate_data():
    db = SessionLocal()
    try:
        logger.info("--- Populating Fleet Data ---")

        # 1. Get Client
        client = db.query(Client).first()
        if not client:
             client = Client(name="FleetSimClient")
             db.add(client)
             db.commit()
             db.refresh(client)
        
        logger.info(f"Using Client ID: {client.id}")
        
        # 2. Create Agents
        # Agent 1: Healthy
        agent1_id = str(uuid.uuid4())
        agent1 = Agent(id=agent1_id, client_id=client.id, hostname="agent-healthy", name="Agent Healthy", status="online", version="1.0.0")
        db.add(agent1)
        
        # Agent 2: Warning (High CPU)
        agent2_id = str(uuid.uuid4())
        agent2 = Agent(id=agent2_id, client_id=client.id, hostname="agent-cpu-warn", name="Agent Warning", status="online", version="1.0.0")
        db.add(agent2)
        
        # Agent 3: Critical (Offline)
        agent3_id = str(uuid.uuid4())
        agent3 = Agent(id=agent3_id, client_id=client.id, hostname="agent-offline", name="Agent Offline", status="offline", version="0.9.0")
        db.add(agent3)
        
        db.commit()

        # 3. Add Telemetry
        processor = AgentTelemetryProcessor(db)
        
        # Healthy
        processor.update_agent_status(agent1_id, {
            "agent_id": agent1_id, "status": "online", "hostname": "agent-healthy", "ip": "10.0.0.1",
            "cpu": 15.0, "ram": 30.0, "version": "1.0.0"
        })
        
        # Warning
        processor.update_agent_status(agent2_id, {
            "agent_id": agent2_id, "status": "online", "hostname": "agent-cpu-warn", "ip": "10.0.0.2",
            "cpu": 92.0, "ram": 45.0, "version": "1.0.0"
        })
        
        # Critical (Offline - Backdated)
        processor.update_agent_status(agent3_id, {
            "agent_id": agent3_id, "status": "online", "hostname": "agent-offline", "ip": "10.0.0.3",
            "cpu": 0.0, "ram": 0.0, "version": "0.9.0"
        })
        # Manually backdate and set critical
        status3 = db.query(AgentStatus).filter(AgentStatus.agent_id == agent3_id).first()
        from datetime import timedelta
        status3.last_seen = datetime.now(timezone.utc) - timedelta(hours=2)
        status3.health_state = "critical"
        
        # Add Alert
        alert = FleetAlert(
            id=str(uuid.uuid4()),
            agent_id=agent3_id,
            client_id=client.id,
            alert_type="agent_offline",
            severity="critical",
            message="Agent is offline for more than 1 hour",
            resolved=False
        )
        db.add(alert)
        db.commit()
        
        logger.info("--- Data Populated Successfully ---")
        
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_data()
