import time
import socket
import platform
import threading
from ..config import config
from .logger import logger
from .api import api_client

class AgentLifecycle:
    def __init__(self):
        self.running = False
        self._stop_event = threading.Event()

    def start(self):
        """Starts the main agent loop."""
        logger.info("Starting Agent Lifecycle...")
        self.running = True

        # 0. Check for Update State (Post-Boot)
        self._check_update_resolution()
        
        # 1. Registration Check
        if not config.agent_id:
            logger.info("Agent not registered. Initiating registration...")
            hostname = socket.gethostname()
            # Basic IP detection (will be improved in Block 2)
            try:
                ip = socket.gethostbyname(hostname)
            except:
                ip = "127.0.0.1"
                
            os_info = f"{platform.system()} {platform.release()}"
            
            if not api_client.register(hostname, ip, os_info):
                logger.critical("Failed to register agent. Exiting loop.")
                self.running = False
                return

        # 2. Main Loop
        self.loop()

    def stop(self):
        """Stops the agent loop."""
        logger.info("Stopping Agent Lifecycle...")
        self.running = False
        self._stop_event.set()

    def loop(self):
        """Heartbeat and Job Processing Loop."""
        logger.info("Entering main loop.")
        while self.running and not self._stop_event.is_set():
            try:
                # Heartbeat
                response = api_client.heartbeat()
                pending_jobs = response.get("pending_jobs", [])
                
                if pending_jobs:
                    logger.info(f"Received pending jobs: {pending_jobs}")
                    for job_id in pending_jobs:
                        self.process_job(job_id)
                
                # Auto-Update Check (Simplified for Demo: Check every loop or N loops)
                # Ideally every few hours. Here every loop (10s) is too much.
                # Let's check every 6th loop (~1 min) for demo purposes, or use a timer.
                self._check_update_safe()

                # Sleep with interrupt check
                self._stop_event.wait(timeout=10) 

    def _check_update_safe(self):
        try:
            from ..modules import updater
            metadata = updater.check_for_update()
            if metadata:
                updater.perform_update(metadata)
        except Exception as e:
            logger.error(f"Update check error: {e}")

    def process_job(self, job_id: str):
        """Orchestrates job execution."""
        from ..modules import scanner # Lazy import
        
        # 1. ACK
        if not api_client.ack_job(job_id):
            logger.error(f"Could not ACK job {job_id}. Skipping execution.")
            return

        # 2. Execute (Hardcoded for Block 3 MVP)
        # Ideally fetch job details first, but pending_jobs list just gives IDs in current API contract.
        # We assume for this block it's a port scan or we just run it.
        # REALITY CHECK: We need to know the job TYPE.
        # The API 'list_agent_jobs' logic in router returns full objects if we query it, 
        # OR the heartbeat returns just IDs. 
        # Let's FETCH job details first if we only have IDs, OR assume heartbeat returned objects.
        # Checking router code... 'HeartbeatResponse' returns 'pending_jobs: List[str]'.
        # We need to GET /jobs to get details, OR just execute generic scan for MVP.
        
        # FOR MVP: We will simply run the 'basic_scan' for ANY job ID received.
        # In a real agent, we query GET /api/agents/jobs to see types.
        
        logger.info(f"Processing Job {job_id} (Assuming basic_scan for MVP)")
        
        try:
            scan_data = scanner.scan_local_ports()
            
            # Summary stats
            tcp_count = len([x for x in scan_data if x['protocol'] == 'tcp'])
            udp_count = len([x for x in scan_data if x['protocol'] == 'udp'])
            
            summary = {
                "total_ports": len(scan_data),
                "tcp": tcp_count,
                "udp": udp_count
            }
            
            # 3. Send Result
            api_client.send_job_result(job_id, {"ports": scan_data}, summary=summary)
            logger.info(f"Job {job_id} completed successfully.")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            api_client.send_job_result(job_id, {"error": str(e)}, status="error")

    def _check_update_resolution(self):
        """Checks if we just recovered from an update or rollback."""
        try:
            import json
            import os
            import sys
            
            if not getattr(sys, 'frozen', False):
                return

            dir_name = os.path.dirname(sys.executable)
            state_file = os.path.join(dir_name, "update_state.json")
            
            if os.path.exists(state_file):
                with open(state_file, "r") as f:
                    state = json.load(f)
                
                status = state.get("status")
                target = state.get("target_version")
                
                if status == "pending":
                    # We are running! That implies success (at least we booted).
                    # Helper verifies persistence, but we can verify logic here.
                    if config.version == target:
                        logger.info(f"Update to {target} successful.")
                        api_client.send_event("update_success", {"version": target})
                        # Update state to done or remove
                        with open(state_file, "w") as f:
                            json.dump({"status": "done", "version": target}, f)
                    else:
                        # Version doesn't match? Maybe rollback happened silently?
                        # Or we are the OLD version starting up after rollback.
                        logger.warning(f"Update pending for {target} but running {config.version}. Rollback likely occurred.")
                        api_client.send_event("update_rollback_detected", {"current_version": config.version, "failed_target": target})
                        os.remove(state_file) # Clear state to avoid loops
                elif status == "done":
                    pass 
        except Exception as e:
            logger.error(f"Error checking update state: {e}")
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)

lifecycle = AgentLifecycle()
