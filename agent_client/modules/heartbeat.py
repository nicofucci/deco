import logging
import time
from modules.http_client import HTTPClient
from modules.agent_id import AgentIdentity
from modules.discovery import NetworkDiscovery

logger = logging.getLogger(__name__)

class Heartbeat:
    def __init__(self):
        self.client = HTTPClient()
        self.identity = AgentIdentity()
        self.discovery = NetworkDiscovery()

    def send(self):
        agent_id = self.identity.get_id()
        if not agent_id:
            logger.warning("Cannot send heartbeat: Agent not registered.")
            return False

        data = self.identity.get_info()
        data["agent_id"] = agent_id
        data["status"] = "online"
        
        # Add Network Info
        try:
            network_info = self.discovery.get_network_info()
            data.update(network_info)
        except Exception as e:
            logger.error(f"Failed to add network info to heartbeat: {e}")
        
        response = self.client.post("/api/agents/heartbeat", data)
        if response:
            logger.debug("Heartbeat sent successfully.")
            return True
        return False
