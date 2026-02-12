import requests
import json
import uuid

# Configuration
API_URL = "http://127.0.0.1:18001"
# Use the API Key we found earlier for "iMac" client
API_KEY = "ce640e924b66f8be765dc632b123bcca" 

def simulate_job_result():
    # 1. Register a dummy agent to get an ID (or use existing if we knew it)
    print("Registering dummy agent...")
    register_payload = {
        "hostname": "SimulatedAgent",
        "version": "2.1.0",
        "os": "Linux",
        "arch": "x64"
    }
    headers = {"X-Client-API-Key": API_KEY}
    
    try:
        res = requests.post(f"{API_URL}/api/agents/register", json=register_payload, headers=headers)
        if res.status_code != 201:
            print(f"Registration failed: {res.text}")
            return
        
        agent_data = res.json()
        agent_id = agent_data["agent_id"]
        print(f"Agent Registered: {agent_id}")
        
        # 2. Create a dummy job (manually in DB or just fake the ID if backend allows unsolicited results? 
        # Backend checks if job exists. So we must create one.)
        # Actually, let's just try to send a result for a non-existent job and see if it 404s (validates connection)
        # OR create a job via API if possible.
        
        # Let's try to create a job via the panel API (requires panel key, which we might not have easily).
        # Alternatively, we can insert a job into the DB directly using python script.
        
        # For now, let's just check if we can hit the endpoint.
        
        fake_job_id = str(uuid.uuid4())
        
        result_payload = {
            "job_id": fake_job_id,
            "agent_id": agent_id,
            "status": "done",
            "data": {
                "cidr": "192.168.1.0/24",
                "hosts": [
                    {"ip": "192.168.1.1", "hostname": "Router", "open_ports": [80, 443]},
                    {"ip": "192.168.1.10", "hostname": "PC-1", "open_ports": [3389]}
                ],
                "count": 2
            }
        }
        
        print(f"Sending result for fake job {fake_job_id}...")
        res = requests.post(f"{API_URL}/api/agents/job_result", json=result_payload, headers=headers)
        
        print(f"Response: {res.status_code} - {res.text}")
        if res.status_code == 404 and "Job no encontrado" in res.text:
            print("SUCCESS: Backend received request and correctly identified missing job.")
        elif res.status_code == 200:
            print("SUCCESS: Result accepted.")
        else:
            print("FAILURE: Unexpected response.")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    simulate_job_result()
