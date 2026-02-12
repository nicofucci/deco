import os
import sys

# Default configuration
DEFAULT_ORCHESTRATOR_URL = "http://localhost:18001"
DEFAULT_HEARTBEAT_INTERVAL = 30

class Config:
    def __init__(self):
        self.orchestrator_url = os.getenv("ORCH_URL", DEFAULT_ORCHESTRATOR_URL)
        self.client_api_key = os.getenv("CLIENT_API_KEY")
        self.agent_id = None
        self.heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", DEFAULT_HEARTBEAT_INTERVAL))
        
        # Load from file if exists (e.g. /etc/deco-agent/config.env or local .env)
        # Simple parser for MVP
        self._load_from_file("config.env")
        self._load_from_file("/etc/deco-agent/config.env")

    def _load_from_file(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        if key == "ORCH_URL":
                            self.orchestrator_url = value
                        elif key == "CLIENT_API_KEY":
                            self.client_api_key = value
                        elif key == "HEARTBEAT_INTERVAL":
                            self.heartbeat_interval = int(value)
                        elif key == "AGENT_ID":
                            self.agent_id = value

    def save_agent_id(self, agent_id):
        self.agent_id = agent_id
        # Persist to local file for MVP
        with open("agent_id.txt", "w") as f:
            f.write(agent_id)

    def load_agent_id(self):
        if os.path.exists("agent_id.txt"):
            with open("agent_id.txt", "r") as f:
                self.agent_id = f.read().strip()

config = Config()
config.load_agent_id()
