import requests
import json
import time
import socket
import platform
from ..config import config
from .logger import logger

class APIClient:
    def __init__(self):
        self.base_url = config.api_url.rstrip('/')
        self.session = requests.Session()
        # Default timeouts
        self.timeout = 10

    def _get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"DecoAgent/{config.version} ({platform.system()})"
        }
        if config.api_key:
            headers["X-Client-API-Key"] = config.api_key
        return headers

    def register(self, hostname: str, ip: str, os_info: str) -> bool:
        """Registers the agent with the tower."""
        endpoint = f"{self.base_url}/api/agents/register"
        payload = {
            "hostname": hostname,
            "ip": ip,
            "version": config.version,
            # os_info logic can be expanded
        }
        
        try:
            logger.info(f"Attempting registration at {endpoint}...")
            response = self.session.post(
                endpoint, 
                json=payload, 
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            agent_id = data.get("agent_id")
            
            if agent_id:
                config.agent_id = agent_id
                config.save()
                logger.info(f"Registration successful. Agent ID: {agent_id}")
                return True
            else:
                logger.error("Registration response missing agent_id")
                return False

        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False

    def heartbeat(self, status: str = "online", metrics: dict = None) -> dict:
        """Sends heartbeat and retrieves pending jobs."""
        if not config.agent_id:
            logger.warning("Agent ID missing. Cannot send heartbeat.")
            return {}
            
        # Lazy import to avoid circular dependency if any
        from ..modules import discovery

        endpoint = f"{self.base_url}/api/agents/heartbeat"
        
        # Gather Real Data
        payload = {
            "agent_id": config.agent_id,
            "status": status,
            "version": config.version,
            "hostname": discovery.get_hostname(),
            "local_ip": discovery.get_primary_ip(),
            "interfaces": discovery.get_network_info(),
            # "system_info": discovery.get_system_info() # If backend supports it
        }
        if metrics:
            payload.update(metrics)

        try:
            logger.debug(f"Sending heartbeat to {endpoint}")
            response = self.session.post(
                endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            return {}

api_client = APIClient()
    def heartBeat(self, status: str = "online", metrics: dict = None) -> dict:
        # ... existing ...
        pass

    def ack_job(self, job_id: str) -> bool:
        """Acknowledges a job start."""
        endpoint = f"{self.base_url}/api/agents/jobs/{job_id}/ack"
        try:
            logger.info(f"ACK Job {job_id}")
            # Ensure headers properly set with current context if needed
            response = self.session.post(
                endpoint, 
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to ACK job {job_id}: {e}")
            return False

    def send_job_result(self, job_id: str, data: dict, summary: dict = None, status: str = "done") -> bool:
        """Sends job results to the tower."""
        endpoint = f"{self.base_url}/api/agents/job_result" # Legacy endpoint supported by router
        payload = {
            "job_id": job_id,
            "agent_id": config.agent_id,
            "status": status,
            "data": data,
            "summary": summary or {}
        }
        
        try:
            logger.info(f"Sending results for Job {job_id} ({len(json.dumps(data))} bytes)")
            response = self.session.post(
                endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send job result {job_id}: {e}")
            return False

    def send_event(self, event_type: str, details: dict) -> bool:
        """Sends a telemetry/audit event to the tower."""
        endpoint = f"{self.base_url}/api/agents/events"
        payload = {
            "agent_id": config.agent_id,
            "event_type": event_type, # e.g., "update_started", "update_success", "update_rollback"
            "details": details,
            "timestamp": time.time()
        }
        try:
            # We fire and forget mostly, but logging implies reliability
            self.session.post(
                endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=5
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to send event {event_type}: {e}")
            return False
