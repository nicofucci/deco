import requests
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .utils import setup_logging

logger = setup_logging("DecoAPI")

class APIClient:
    def __init__(self, config):
        self.config = config
        self.session = self._create_session()
    
    def _create_session(self):
        """
        Crea una sesión con estrategia de reintentos robusta (Exponential Backoff).
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1, # 1s, 2s, 4s, 8s, 16s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _get_headers(self):
        return {
            "X-Client-API-Key": self.config.api_key,
            "Content-Type": "application/json",
            "User-Agent": "DecoSecurityAgent/2.1.0 (Windows)"
        }

    def _get_url(self, endpoint):
        base = self.config.orchestrator_url.rstrip("/")
        path = endpoint.lstrip("/")
        return f"{base}/{path}"

    def register(self, payload):
        """
        Registra el agente en el Orchestrator.
        """
        url = self._get_url("/api/agents/register")
        try:
            # Para registro usamos headers sin API Key si es el primer paso, 
            # pero el diseño actual requiere API Key del cliente para registrar.
            # Asumimos que config.api_key ya tiene la key del cliente.
            res = self.session.post(url, json=payload, headers=self._get_headers(), timeout=15)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return None

    def send_heartbeat(self, payload):
        """
        Envía heartbeat y recibe jobs pendientes.
        """
        url = self._get_url("/api/agents/heartbeat")
        try:
            res = self.session.post(url, json=payload, headers=self._get_headers(), timeout=10)
            if res.status_code == 200:
                return res.json() # Returns dict with 'pending_jobs'
            else:
                logger.warning(f"Heartbeat failed with status {res.status_code}: {res.text}")
                return None
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return None

    def get_jobs(self, agent_id):
        """
        Obtiene la lista detallada de jobs pendientes.
        """
        url = self._get_url(f"/api/agents/jobs?agent_id={agent_id}")
        try:
            res = self.session.get(url, headers=self._get_headers(), timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            return None

    def send_job_result(self, result_payload):
        """
        Envía el resultado de un job.
        """
        url = self._get_url("/api/agents/job_result")
        try:
            res = self.session.post(url, json=result_payload, headers=self._get_headers(), timeout=30)
            res.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error sending job result: {e}")
            return False

    def download_file(self, url, dest_path):
        """
        Descarga un archivo (para auto-update).
        """
        try:
            with self.session.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {e}")
            return False
