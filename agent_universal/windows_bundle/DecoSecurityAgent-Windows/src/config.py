import os
import json
import platform
import logging

logger = logging.getLogger("DecoConfig")

# Constants
DEFAULT_ORCHESTRATOR_URL = "http://127.0.0.1:8001"
ORCHESTRATOR_URL = os.environ.get("DECO_ORCHESTRATOR_URL", DEFAULT_ORCHESTRATOR_URL)
AGENT_VERSION = "2.0.0-universal"

class Config:
    def __init__(self):
        self.os_type = platform.system()
        self.config_path = self._get_config_path()
        self.api_key = None
        self.agent_id = None
        self.load()

    def _get_config_path(self):
        if self.os_type == "Windows":
            program_data = os.environ.get("ProgramData", "C:\\ProgramData")
            return os.path.join(program_data, "DecoSecurityAgent", "config.json")
        else:
            # Linux / Unix
            # Check /etc first, then local fallback
            if os.path.exists("/etc/deco-security-agent/config.json"):
                return "/etc/deco-security-agent/config.json"
            return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key")
                    self.agent_id = data.get("agent_id")
            except Exception as e:
                logger.error(f"Error loading config: {e}")

    def save(self):
        data = {
            "api_key": self.api_key,
            "agent_id": self.agent_id
        }
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def set_api_key(self, key):
        self.api_key = key
        self.save()

    def set_agent_id(self, agent_id):
        self.agent_id = agent_id
        self.save()
