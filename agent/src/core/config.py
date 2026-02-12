import os
import yaml
from pydantic import BaseModel
from typing import Optional

class AgentConfig(BaseModel):
    orchestrator_url: str = "http://localhost:19001"
    client_api_key: str
    agent_id: Optional[str] = None
    log_level: str = "INFO"
    heartbeat_interval: int = 30
    job_check_interval: int = 60

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Optional[AgentConfig] = None

    def load(self) -> AgentConfig:
        # 1. Try loading from file
        file_config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                file_config = yaml.safe_load(f) or {}

        # 2. Override with Env Vars
        env_config = {}
        if os.getenv("DECO_ORCHESTRATOR_URL"):
            env_config["orchestrator_url"] = os.getenv("DECO_ORCHESTRATOR_URL")
        if os.getenv("DECO_CLIENT_API_KEY"):
            env_config["client_api_key"] = os.getenv("DECO_CLIENT_API_KEY")
        if os.getenv("DECO_AGENT_ID"):
            env_config["agent_id"] = os.getenv("DECO_AGENT_ID")

        # Merge: File < Env
        final_config = {**file_config, **env_config}
        
        # Validate
        try:
            self.config = AgentConfig(**final_config)
            return self.config
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")

    def save_agent_id(self, agent_id: str):
        """Persist agent_id to config file"""
        if self.config:
            self.config.agent_id = agent_id
        
        # Read existing to preserve comments/structure if possible (YAML is tricky, simple dump for now)
        current_data = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                current_data = yaml.safe_load(f) or {}
        
        current_data["agent_id"] = agent_id
        
        with open(self.config_path, "w") as f:
            yaml.dump(current_data, f)

# Global instance
config_loader = ConfigLoader()
