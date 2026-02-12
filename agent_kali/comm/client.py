import requests
import json
import time
from typing import Dict, Any, Optional

class DecoClient:
    def __init__(self, orchestrator_url: str, api_key: Optional[str] = None):
        self.base_url = orchestrator_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-Client-API-Key": api_key})

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        self.session.headers.update({"X-Client-API-Key": api_key})

    def register_agent(self, hostname: str, version: str, os_info: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/agents/register"
        payload = {
            "hostname": hostname,
            "version": version,
            "os_info": os_info
        }
        try:
            resp = self.session.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error registering agent: {e}")
            return None

    def send_heartbeat(self, agent_id: str, status: str = "online") -> Dict[str, Any]:
        url = f"{self.base_url}/api/agents/heartbeat"
        payload = {
            "agent_id": agent_id,
            "status": status
        }
        try:
            resp = self.session.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error sending heartbeat: {e}")
            return None

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        # En la API actual no hay un endpoint específico para GET /jobs/{id} público para agentes,
        # pero el heartbeat nos dice qué jobs hay.
        # Asumiremos que el agente recibe la info del job de alguna manera o que implementamos un GET.
        # Por ahora, si el heartbeat solo devuelve IDs, necesitamos un endpoint para bajar el job.
        # REVISIÓN: En fases anteriores, el heartbeat devolvía 'pending_jobs': [id].
        # Falta un endpoint para que el agente obtenga los detalles del job (target, type).
        # Voy a asumir que existe o lo simularé.
        # Si no existe, tendré que usar el listado de jobs filtrado (que requiere auth de cliente).
        # El agente usa la API Key del cliente, así que puede listar jobs.
        
        url = f"{self.base_url}/api/jobs"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            jobs = resp.json()
            for job in jobs:
                if job["id"] == job_id:
                    return job
            return None
        except requests.RequestException as e:
            print(f"Error fetching job details: {e}")
            return None

    def upload_result(self, job_id: str, agent_id: str, raw_data: Dict[str, Any], summary: Dict[str, Any]) -> bool:
        url = f"{self.base_url}/api/results"
        payload = {
            "scan_job_id": job_id,
            "agent_id": agent_id,
            "raw_data": raw_data,
            "summary": summary
        }
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error uploading result: {e}")
            return False
