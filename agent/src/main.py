import time
import sys
import os

# Add src to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import config_loader
from core.logger import logger

def main():
    logger.info("🚀 Starting Deco-Security Agent...")

    try:
        config = config_loader.load()
        logger.info(f"Configuration loaded. Orchestrator: {config.orchestrator_url}")
    except Exception as e:
        logger.critical(f"Failed to load configuration: {e}")
        sys.exit(1)

    if not config.client_api_key:
        logger.critical("Client API Key is missing. Please set DECO_CLIENT_API_KEY or update config.yaml")
        sys.exit(1)

    logger.info("Agent initialized successfully.")
    
    # Main Loop Placeholder
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Agent stopping...")

if __name__ == "__main__":
    main()
