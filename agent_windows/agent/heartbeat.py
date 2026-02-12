import platform
import logging
import uuid
from agent.network import NetworkService
from agent.api import APIClient
from agent.utils import setup_logging

logger = setup_logging("DecoHeartbeat")

class HeartbeatService:
    def __init__(self, config, api_client: APIClient):
        self.config = config
        self.api = api_client
        self.network = NetworkService()

    def register(self):
        if self.config.agent_id:
            logger.info(f"Agent already registered with ID: {self.config.agent_id}")
            return True

        logger.info("Registering agent...")
        hostname = platform.node()
        payload = {
            "hostname": hostname,
            "version": "2.1.0-windows", 
            "os": platform.system(),
            "arch": platform.machine()
        }

        data = self.api.register(payload)
        if data and "agent_id" in data:
            self.config.set_agent_id(data["agent_id"])
            logger.info(f"Registration successful. ID: {data['agent_id']}")
            return True
        else:
            logger.error("Registration failed.")
            return False

    def send_heartbeat(self):
        if not self.config.agent_id:
            logger.warning("Cannot send heartbeat: Agent not registered.")
            return None

        # Gather info (Robust Network Info)
        network_info = self.network.get_network_info()
        
        payload = {
            "agent_id": self.config.agent_id,
            "status": "online",
            "local_ip": network_info.get("local_ip"),
            "primary_cidr": network_info.get("primary_cidr"),
            "interfaces": network_info.get("interfaces", [])
        }

        data = self.api.send_heartbeat(payload)
        if data:
            pending_jobs = data.get("pending_jobs", [])
            if pending_jobs:
                logger.info(f"Heartbeat OK. Jobs received: {len(pending_jobs)}")
            return pending_jobs
        else:
            return None
