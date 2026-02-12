import requests
import json
from typing import Optional, Dict, Any
from core.config import AgentConfig, config_loader
from core.logger import logger
from core.security import get_system_info

class APIClient:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.base_url = config.orchestrator_url.rstrip("/")
        self.session = requests.Session()
        # For MVP, disable SSL verification warnings if needed
        if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            self.verify_ssl = False
        else:
            self.verify_ssl = True

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Client-API-Key": self.config.client_api_key
        }
        if self.config.agent_id:
            headers["X-Agent-ID"] = self.config.agent_id
        return headers

    def register(self) -> bool:
        """
        Registers the agent with the Orchestrator.
        Updates config with the received agent_id.
        """
        url = f"{self.base_url}/api/agents/register"
        payload = get_system_info()
        
        try:
            logger.info(f"Registering agent at {url}...")
            response = self.session.post(
                url, 
                json=payload, 
                headers=self._get_headers(), 
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_id = data.get("agent_id")
                if agent_id:
                    logger.info(f"Registration successful! Agent ID: {agent_id}")
                    # Persist Agent ID
                    config_loader.save_agent_id(agent_id)
                    # Update local config instance
                    self.config.agent_id = agent_id
                    return True
                else:
                    logger.error(f"Registration response missing agent_id: {data}")
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            
        return False

    def send_heartbeat(self, status: str = "online", metrics: Dict = None) -> Dict:
        """
        Sends heartbeat to Orchestrator.
        Returns response data (which might include pending jobs).
        """
        if not self.config.agent_id:
            logger.warning("Cannot send heartbeat: Agent not registered.")
            return {}

        url = f"{self.base_url}/api/agents/heartbeat"
        payload = {
            "agent_id": self.config.agent_id,
            "status": status,
            "metrics": metrics or {}
        }

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Heartbeat failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            
        return {}

# Factory
def get_api_client() -> APIClient:
    config = config_loader.load()
    return APIClient(config)
