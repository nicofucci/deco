import json
import os
import logging
from pathlib import Path
from config import CONFIG_FILE, init_dirs

logger = logging.getLogger(__name__)

class SecureStorage:
    def __init__(self):
        init_dirs()
        self.config_file = CONFIG_FILE

    def load_config(self):
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def save_config(self, config_data):
        try:
            # Merge with existing
            current = self.load_config()
            current.update(config_data)
            
            # Write securely (restrict permissions on Linux)
            with open(self.config_file, 'w') as f:
                json.dump(current, f, indent=4)
            
            if os.name == 'posix':
                os.chmod(self.config_file, 0o600)
                
            logger.info("Configuration saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get(self, key, default=None):
        config = self.load_config()
        return config.get(key, default)

    def set(self, key, value):
        return self.save_config({key: value})
