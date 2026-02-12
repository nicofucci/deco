import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add orchestrator path
sys.path.append("/opt/deco/tower/orchestrator")

from app.models.domain import Client, Agent
from app.db.session import SessionLocal

def debug_api_key(api_key):
    db = SessionLocal()
    try:
        print(f"--- DEBUGGING API KEY: {api_key} ---")
        
        # 1. Search in Client table (agent_api_key)
        client = db.query(Client).filter(Client.agent_api_key == api_key).first()
        if client:
            print(f"[SUCCESS] Found Client for Agent API Key!")
            print(f"  Client ID: {client.id}")
            print(f"  Name: {client.name}")
            print(f"  Status: {client.status}")
            
            # Check agents for this client
            agents = db.query(Agent).filter(Agent.client_id == client.id).all()
            print(f"  Registered Agents: {len(agents)}")
            for a in agents:
                print(f"    - {a.hostname} (ID: {a.id}) Status: {a.status} Last Seen: {a.last_seen_at}")
        else:
            print(f"[ERROR] API Key NOT found in Client table (agent_api_key).")
            
            # Check if it might be a client_panel_api_key by mistake
            client_panel = db.query(Client).filter(Client.client_panel_api_key == api_key).first()
            if client_panel:
                print(f"[WARNING] Key found as 'client_panel_api_key' for client {client_panel.name}. The agent might be using the WRONG key type.")

    except Exception as e:
        print(f"[EXCEPTION] {e}")
    finally:
        db.close()

def debug_scheduler_logic():
    print("\n--- DEBUGGING SCHEDULER LOGIC ---")
    from app.services.scheduler import check_agent_health
    try:
        print("Running check_agent_health() manually...")
        check_agent_health()
        print("Manual execution finished. Check logs if possible.")
    except Exception as e:
        print(f"[EXCEPTION] Scheduler logic failed: {e}")

if __name__ == "__main__":
    target_key = "ce640e924b66f8be765dc632b123bcca"
    debug_api_key(target_key)
    debug_scheduler_logic()
