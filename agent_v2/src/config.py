import os
import json
import sys
from typing import Dict, Any

class Config:
    def __init__(self):
        self.api_url = "https://api.deco-security.com"
        self.api_key = ""
        self.agent_id = ""
        self.log_level = "INFO"
        self.version = "2.0.0-demo"
        self.auto_update_enabled = True
        
        # Paths
        if os.name == 'nt':
            self.program_data = os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'DecoSecurity')
        else:
            self.program_data = "/opt/deco/agent_data" # Dev path
            
        self.config_path = os.path.join(self.program_data, "config.json")
        self.log_path = os.path.join(self.program_data, "logs")
        
        self.load()

    def load(self):
        """Loads configuration from disk."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.api_url = data.get("api_url", self.api_url)
                    self.api_key = data.get("api_key", self.api_key)
                    self.agent_id = data.get("agent_id", self.agent_id)
                    self.log_level = data.get("log_level", self.log_level)
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            print("Config file not found. Using defaults.")

    def save(self):
        """Saves current configuration to disk."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        data = {
            "api_url": self.api_url,
            "api_key": self.api_key,
            "agent_id": self.agent_id,
            "log_level": self.log_level
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

# Global instance
config = Config()
