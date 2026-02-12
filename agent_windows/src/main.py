import time
import sys
import logging
from config import Config
from api import APIClient
from utils import setup_logging
from services.heartbeat import HeartbeatService
from services.jobs import JobService

def run_agent():
    logger = setup_logging("DecoAgentMain")
    logger.info("Deco-Security Universal Agent Starting (v2.1.0)...")

    # 1. Load Config
    config = Config()
    
    # 2. Check API Key Loop
    # In service mode, we might start before config is written by installer.
    # Wait for API Key.
    while not config.api_key:
        logger.warning("No API Key found. Waiting for configuration...")
        time.sleep(10)
        config.load() # Reload config to check if file appeared

    logger.info(f"API Key found. Orchestrator: {config.orchestrator_url}")

    # 3. Services Init
    api_client = APIClient(config)
    heartbeat = HeartbeatService(config, api_client)
    jobs = JobService(config, api_client)

    # 4. Registration Loop
    while True:
        if heartbeat.register():
            break
        logger.error("Registration failed. Retrying in 30 seconds...")
        time.sleep(30)

    # 5. Main Loop
    logger.info("Entering main loop...")
    error_count = 0
    
    while True:
        try:
            # Heartbeat
            pending_jobs = heartbeat.send_heartbeat()
            
            if pending_jobs is not None:
                error_count = 0 # Reset error count on success
                
                # Jobs
                if pending_jobs:
                    jobs.process_jobs(pending_jobs)
            else:
                error_count += 1
                logger.warning(f"Heartbeat failed (Count: {error_count})")
            
            # Backoff logic
            sleep_time = 20 if error_count < 5 else 60
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("Stopping agent...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_agent()
