
import requests
import json
import time
import sys
import uuid

# Config
API_URL = "http://localhost:8000/api"
CLIENT_ID = "45a5391a-a4fa-4364-84f0-1aa8c0dab72e"
AGENT_HOSTNAME = "Leoslo"
AGENT_ID = "375a73bc-1d2c-4fbf-ae8e-3f971b0ec96e"
AGENT_KEY = "4d79a5259226b6cf148be65138add7a2" 

def run_simulation():
    print(f"--- Simulating Agent {AGENT_HOSTNAME} ---")
    headers = {"X-Client-API-Key": AGENT_KEY}

    # 1. Register/Activate (Ensure online)
    print("[1] Registering...")
    reg_payload = {
        "hostname": AGENT_HOSTNAME,
        "version": "3.0.0-sim",
        "ip": "192.168.100.10",
        "primary_cidr": "192.168.100.0/24"
    }
    resp = requests.post(f"{API_URL}/agents/register", json=reg_payload, headers=headers)
    if resp.status_code not in [200, 201]:
        print(f"Register failed: {resp.text}")
        return
    print(f"    Register OK.")

    # 2. Trigger a fresh job manually via API (simulating that the partner requested it or it was scheduled)
    # Actually, we can just POST a result for a fake job ID if we want, OR we can fetch the 'pending' job if one exists.
    # The previous job `da64dac2` failed.
    # Let's create a NEW job via DB insert helper or just POST a result saying it's for a new job.
    # But for robustness, let's just insert a job via SQL first?
    # No, I can't easily do SQL from python without sqlalchemy.
    # I'll just post a result with a random UUID. The backend might accept it if it blindly trusts key.
    # Wait, `persist_result_job` checks if job exists.
    # So I need a valid job ID.
    
    # Let's FETCH jobs. Maybe there is one pending?
    print("[2] Heartbeat (Fetching Jobs)...")
    hb_payload = {
        "agent_id": AGENT_ID,
        "status": "online",
        "load_avg": 0.5,
        "memory_usage": 40.0
    }
    resp = requests.post(f"{API_URL}/agents/heartbeat", json=hb_payload, headers=headers)
    jobs = resp.json().get("pending_jobs", [])
    print(f"    Pending Jobs: {jobs}")

    job_id = None
    if jobs:
        job_id = jobs[0]
    else:
        print("    No jobs found. Cannot post result without a job.")
        print("    Please run trigger_discovery.py first to queue a job.")
        return

    # 3. ACK
    print(f"[3] Processing Job {job_id}...")
    requests.post(f"{API_URL}/agents/jobs/{job_id}/ack", headers=headers)
    
    time.sleep(1)
    
    # 4. Post Results (X-RAY Network Scan)
    print(f"[4] Posting Results for {job_id}...")
    
    scan_data = {
        "devices": [
            {"ip": "192.168.100.1", "hostname": "Gateway-Router", "mac": "00:11:22:33:44:55", "os_guess": "Linux/OpenWrt", "type": "router", "open_ports": [80, 443, 53]},
            {"ip": "192.168.100.10", "hostname": "Leoslo-Thinkpad", "mac": "AA:BB:CC:DD:EE:FF", "os_guess": "Windows 10 Pro", "type": "pc", "open_ports": [135, 139, 445, 3389]},
            {"ip": "192.168.100.50", "hostname": "Office-Printer", "mac": "11:22:33:44:55:66", "os_guess": "HP JetDirect", "type": "printer", "open_ports": [9100, 80]},
            {"ip": "192.168.100.200", "hostname": "NAS-Storage", "mac": "22:33:44:55:66:77", "os_guess": "Synology DSM", "type": "server", "open_ports": [80, 5000, 445, 2049]},
            {"ip": "192.168.100.105", "hostname": "iPad-Pro", "mac": "33:44:55:66:77:88", "os_guess": "iOS", "type": "mobile", "open_ports": []},
             {"ip": "192.168.100.120", "hostname": "Smart-TV", "mac": "44:55:66:77:88:99", "os_guess": "Android TV", "type": "iot", "open_ports": [8008, 8009]}
        ],
        "metadata": {"subnet": "192.168.100.0/24", "method": "arp_scan"}
    }
    
    res_payload = {
        "job_id": job_id,
        "agent_id": AGENT_ID,
        "status": "done",
        "data": scan_data
    }
    
    r = requests.post(f"{API_URL}/agents/job_result", json=res_payload, headers=headers)
    print(f"    Result Posted: {r.status_code}")
    if r.status_code != 200:
        print(r.text)

if __name__ == "__main__":
    run_simulation()
