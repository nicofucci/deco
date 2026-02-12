
import requests
import json
import time
import sys

# Config
API_URL = "http://localhost:8000/api"
CLIENT_ID = "656252a8-93c0-439e-a05f-448783e4c96c"
AGENT_HOSTNAME = "DESKTOP-MOCOKOB"
# Gets populated via sys.argv or hardcoded if needed
AGENT_KEY = "" 

def run_simulation(key):
    print(f"--- Simulating Agent {AGENT_HOSTNAME} ---")
    headers = {"X-Client-API-Key": key}

    # 1. Register/Activate (to ensure online)
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
    agent_id = resp.json()["agent_id"]
    print(f"    Agent ID: {agent_id} (Online)")

    # 2. Heartbeat (Get Jobs)
    print("[2] Heartbeat (Fetching Jobs)...")
    hb_payload = {
        "agent_id": agent_id,
        "status": "online",
        "load_avg": 0.5,
        "memory_usage": 40.0
    }
    resp = requests.post(f"{API_URL}/agents/heartbeat", json=hb_payload, headers=headers)
    jobs = resp.json().get("pending_jobs", [])
    print(f"    Pending Jobs: {jobs}")

    if not jobs:
        print("    No jobs found. Did the discovery trigger work?")
        # Just in case, try /agents/jobs directly
        # resp = requests.get(f"{API_URL}/agents/jobs?agent_id={agent_id}", headers=headers)
        # print(f"    Direct Jobs Check: {resp.json()}")

    for job_id in jobs:
        # 3. ACK
        print(f"[3] Processing Job {job_id}...")
        requests.post(f"{API_URL}/agents/jobs/{job_id}/ack", headers=headers)
        
        # Simulate Scan Duration
        time.sleep(1)
        
        # 4. Post Results (X-RAY Network Scan)
        print(f"[4] Posting Results for {job_id}...")
        
        
        scan_data = {
            "devices": [
                {"ip": "192.168.100.1", "hostname": "Gateway-Router", "mac": "00:11:22:33:44:55", "os_guess": "Linux/OpenWrt", "type": "router", "open_ports": [80, 443, 53]},
                {"ip": "192.168.100.10", "hostname": "DESKTOP-MOCOKOB", "mac": "AA:BB:CC:DD:EE:FF", "os_guess": "Windows 10", "type": "pc", "open_ports": [135, 139, 445, 3389]},
                {"ip": "192.168.100.50", "hostname": "Office-Printer", "mac": "11:22:33:44:55:66", "os_guess": "HP JetDirect", "type": "printer", "open_ports": [9100, 80]},
                {"ip": "192.168.100.200", "hostname": "NAS-Storage", "mac": "22:33:44:55:66:77", "os_guess": "Synology DSM", "type": "server", "open_ports": [80, 5000, 445, 2049]},
                {"ip": "192.168.100.105", "hostname": "iPhone-User", "mac": "33:44:55:66:77:88", "os_guess": "iOS", "type": "mobile", "open_ports": []}
            ],
            "metadata": {"subnet": "192.168.100.0/24", "method": "arp_scan"}
        }
        
        res_payload = {
            "job_id": job_id,
            "agent_id": agent_id,
            "status": "done",
            "data": scan_data
        }
        
        r = requests.post(f"{API_URL}/agents/job_result", json=res_payload, headers=headers)
        print(f"    Result Posted: {r.status_code}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simulate.py <API_KEY>")
        sys.exit(1)
    run_simulation(sys.argv[1])
