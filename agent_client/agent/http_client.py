import requests
import json
import platform
import socket
import time
from .config import config

class HTTPClient:
    def __init__(self):
        self.base_url = config.orchestrator_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Client-API-Key": config.client_api_key or ""
        })

    def register(self):
        url = f"{self.base_url}/api/agents/register"
        payload = {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "arch": platform.machine(),
            "version": "1.0.0"
        }
        try:
            print(f"[*] Registering agent at {url}...")
            res = self.session.post(url, json=payload, timeout=10)
            if res.status_code == 201:
                data = res.json()
                config.save_agent_id(data["agent_id"])
                print(f"[+] Registered! Agent ID: {data['agent_id']}")
                return True
            else:
                print(f"[-] Registration failed: {res.text}")
        except Exception as e:
            print(f"[-] Connection error: {e}")
        return False

    def send_heartbeat(self):
        if not config.agent_id:
            return None
        
        url = f"{self.base_url}/api/agents/heartbeat"
        payload = {
            "agent_id": config.agent_id,
            "status": "online",
            "metrics": {} # Future: CPU/RAM
        }
        try:
            res = self.session.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                return res.json() # Returns {status: "ok", pending_jobs: [...]}
        except Exception as e:
            print(f"[-] Heartbeat error: {e}")
        return None

    def get_job(self, job_id):
        url = f"{self.base_url}/api/jobs/{job_id}"
        try:
            res = self.session.get(url, timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"[-] Get Job error: {e}")
        return None

    def upload_result(self, job_id, raw_data, summary=None):
        url = f"{self.base_url}/api/results"
        payload = {
            "scan_job_id": job_id,
            "agent_id": config.agent_id,
            "raw_data": raw_data,
            "summary": summary or {}
        }
        try:
            res = self.session.post(url, json=payload, timeout=10)
            if res.status_code == 201:
                print(f"[+] Result uploaded for Job {job_id}")
                return True
            else:
                print(f"[-] Upload failed: {res.text}")
        except Exception as e:
            print(f"[-] Upload error: {e}")
        return False
