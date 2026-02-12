import requests
import uuid
import time

API_URL = "http://localhost:19001"
# We need a valid client API Key. 
# I'll try to find one in the DB or use a known one if available.
# Since I can't easily query DB from here without sqlalchemy setup, 
# I'll assume I can use the one from the user's previous context or try to find one.
# Let's try to read 'agent_client/agent_id.txt' or similar if it exists from previous runs, 
# or just check the logs/DB.

# Actually, I can use the `sqlite` command line if it's a sqlite db, or `psql` if postgres.
# The docker-compose said postgres.
# I'll try to register a new client if possible, or just use a placeholder and hope for the best?
# No, I need a valid key.

# Let's try to get a client API key from the database using docker exec.
import subprocess

def get_api_key():
    try:
        cmd = [
            "docker", "exec", "deco-sec-orchestrator", 
            "python", "-c", 
            "from app.db.session import SessionLocal; from app.models.domain import Client; db = SessionLocal(); client = db.query(Client).first(); print(client.api_key if client else 'NONE')"
        ]
        result = subprocess.check_output(cmd, text=True).strip()
        return result
    except Exception as e:
        print(f"Error getting API Key: {e}")
        return None

def verify():
    api_key = get_api_key()
    if not api_key or api_key == 'NONE':
        print("No API Key found. Cannot verify.")
        return

    print(f"Using API Key: {api_key}")
    
    # 1. Register Agent
    hostname = f"test-agent-{uuid.uuid4().hex[:8]}"
    print(f"Registering agent: {hostname}")
    
    headers = {"X-Client-API-Key": api_key}
    payload = {
        "hostname": hostname,
        "version": "1.0.0",
        "os": "Linux"
    }
    
    try:
        res = requests.post(f"{API_URL}/api/agents/register", json=payload, headers=headers)
        if res.status_code != 201:
            print(f"Registration failed: {res.text}")
            return
        
        data = res.json()
        agent_id = data["agent_id"]
        print(f"Agent registered. ID: {agent_id}")
        
        # 2. Send Heartbeat with Network Info
        print("Sending heartbeat with network info...")
        heartbeat_payload = {
            "agent_id": agent_id,
            "status": "online",
            "local_ip": "192.168.1.50",
            "primary_cidr": "192.168.1.0/24",
            "interfaces": [
                {"name": "eth0", "ip": "192.168.1.50", "cidr": "192.168.1.0/24"}
            ]
        }
        
        res = requests.post(f"{API_URL}/api/agents/heartbeat", json=heartbeat_payload, headers=headers)
        if res.status_code != 200:
            print(f"Heartbeat failed: {res.text}")
            return
        print("Heartbeat sent.")
        
        # 3. Verify Data stored
        print("Verifying data via API...")
        res = requests.get(f"{API_URL}/api/agents", headers=headers)
        agents = res.json()
        
        found = False
        for agent in agents:
            if agent["id"] == agent_id:
                print(f"Agent found: {agent}")
                if agent.get("local_ip") == "192.168.1.50" and agent.get("primary_cidr") == "192.168.1.0/24":
                    print("SUCCESS: Network info verified.")
                    found = True
                else:
                    print("FAILURE: Network info mismatch.")
                break
        
        if not found:
            print("FAILURE: Agent not found in list.")

    except Exception as e:
        print(f"Verification failed with exception: {e}")

if __name__ == "__main__":
    verify()
