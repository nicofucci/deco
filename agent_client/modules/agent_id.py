import platform
import socket
import uuid
import logging
from modules.http_client import HTTPClient
from modules.secure_storage import SecureStorage
from config import AGENT_VERSION

logger = logging.getLogger(__name__)

class AgentIdentity:
    def __init__(self):
        self.storage = SecureStorage()
        self.client = HTTPClient()

    def get_info(self):
        return {
            "hostname": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
            "version": AGENT_VERSION,
            "ip_list": self._get_ip_addresses()
        }

    def _get_ip_addresses(self):
        try:
            return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
        except:
            return []

    def register(self):
        # Check if already registered
        agent_id = self.storage.get("agent_id")
        if agent_id:
            logger.info(f"Agent already registered with ID: {agent_id}")
            return True

        # Check for API Key
        api_key = self.storage.get("client_api_key")
        if not api_key:
            logger.error("No Client API Key found. Cannot register.")
            return False

        logger.info("Registering agent with Orchestrator...")
        data = self.get_info()
        
        response = self.client.post("/api/agents/register", data)
        
        if response and "agent_id" in response:
            self.storage.save_config({
                "agent_id": response["agent_id"],
                "agent_token": response.get("token", ""), # If backend sends a token
                "status": "registered"
            })
            logger.info(f"Agent successfully registered. ID: {response['agent_id']}")
            return True
        else:
            logger.error("Registration failed.")
            return False

    def get_id(self):
        return self.storage.get("agent_id")
