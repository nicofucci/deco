import requests
import time
import json
import uuid

API_URL = "http://127.0.0.1:8000/api"

def run_simulation():
    print("[*] Starting Specialized Scan Simulation...")
    
    # 1. Get Client & Key (Assuming existing env or DB access, using same hack as before)
    # Actually, let's use the API to list clients if possible, via an admin key or just grab first agent.
    # We'll do the DB hack to get keys.
    from app.db.session import SessionLocal
    from app.models.domain import Client, Agent, NetworkAsset
    db = SessionLocal()
    
    client = db.query(Client).first()
    agent = db.query(Agent).filter(Agent.client_id == client.id).first()
    
    if not client or not agent:
        print("[-] No client/agent found.")
        return

    # Ensure we have an asset
    asset = db.query(NetworkAsset).filter(NetworkAsset.client_id == client.id).first()
    if not asset:
        # Create dummy asset
        asset = NetworkAsset(
            id=str(uuid.uuid4()),
            client_id=client.id,
            ip="192.168.99.100", # Specific test IP
            status="stable",
            hostname="Simulation-IoT-Device"
        )
        db.add(asset)
        db.commit()
        print(f"[+] Created dummy asset {asset.ip}")
    else:
        print(f"[+] Using asset {asset.ip}")

    # 2. Trigger IoT Deep Scan (via API)
    # We need the client Panel Key or Master key?
    # Router uses get_db and depends... check auth.
    # network.py endpoints don't seem to enforce strict auth in code shown (bad practice but useful for test).
    # Wait, they usually have "Depends(get_current_active_user)" or "APIKey".
    # In network.py: "router = APIRouter()". No global dependencies shown. 
    # Let's try raw request. If 401, we might need X-Client-API-Key or similar.
    # Actually, the user prompt implies these are triggered by Console (Partner/Client).
    # Assuming for now we can call them publicly for this test or use a key if needed.
    
    # Let's try to pass X-Client-API-Key just in case.
    headers = {"X-Client-API-Key": client.agent_api_key} # Using Agent key as proxy for auth if needed
    # Actually, orchestration usually uses Master or Partner key.
    # Let's try without auth first (dev mode).
    
    print(f"[*] Triggering IoT Deep Scan for {asset.ip}...")
    payload = {"target_ip": asset.ip}
    res = requests.post(f"{API_URL}/network/clients/{client.id}/jobs/iot-deep-scan", json=payload)
    if res.status_code != 200:
        print(f"[-] Trigger failed: {res.text}")
        return
    
    job = res.json()
    job_id = job["id"]
    print(f"[+] Job Created: {job_id}")
    
    # 3. Simulate Agent Execution (Submit Result)
    # The agent receives the job, runs it, creates a payload.
    # "iot_deep_scan" payload structure.
    
    result_data = {
        "target_ip": asset.ip,
        "firmware": "v1.0.0-vulnerable",
        "admin_panel": True,
        "default_creds": True, # Should trigger Critical severity
        "upnp": {"enabled": True, "services": ["WANIPConnection"]}
    }
    
    job_result_payload = {
        "job_id": job_id,
        "agent_id": agent.id,
        "status": "done",
        "data": result_data
    }
    
    print("[*] Submitting Job Result (Agent Simulation)...")
    res = requests.post(f"{API_URL}/agents/job_result", json=job_result_payload, headers=headers)
    if res.status_code != 200:
        print(f"[-] Submission failed: {res.text}")
        return
    print("[+] Result Submitted.")
    
    # 4. Wait for Processing (Async/Sync)
    time.sleep(2)
    
    # 5. Verify Findings via API
    print("[*] Verifying Findings...")
    res = requests.get(f"{API_URL}/network/clients/{client.id}/specialized-findings?job_type=iot_deep_scan")
    if res.status_code != 200:
        print(f"[-] Verification failed: {res.text}")
        return
        
    findings = res.json()
    # Filter for our asset
    my_findings = [f for f in findings if f["asset_id"] == asset.id]
    
    if my_findings:
        f = my_findings[0]
        print(f"[SUCCESS] Found Finding: {f['id']}")
        print(f" - Severity: {f['severity']}")
        print(f" - Data: {f['data']}")
        
        if f['severity'] == "critical":
            print("[PASS] Severity correctly calculated.")
        else:
            print(f"[FAIL] Expected critical, got {f['severity']}")
    else:
        print("[-] No findings found.")

if __name__ == "__main__":
    run_simulation()
