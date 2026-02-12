import requests
import json
import uuid

API_URL = "http://127.0.0.1:18001"
API_KEY = "ce640e924b66f8be765dc632b123bcca" 

def simulate_discovery_result():
    # 1. Register agent
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
        
        fake_job_id = str(uuid.uuid4())
        
        # Payload mimicking the one that failed (missing hostname)
        result_payload = {
            "job_id": fake_job_id,
            "agent_id": agent_id,
            "status": "done",
            "data": {
                "cidr": "192.168.100.0/24",
                "hosts": [
                    {"ip": "192.168.100.58", "open_ports": [80]} # No hostname provided
                ],
                "count": 1
            }
        }
        
        print(f"Sending result for fake job {fake_job_id}...")
        res = requests.post(f"{API_URL}/api/agents/job_result", json=result_payload, headers=headers)
        
        print(f"Response: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    simulate_discovery_result()
