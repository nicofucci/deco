import logging
import requests
import time
from .network_discovery import NetworkDiscovery

logger = logging.getLogger("DecoAgent.Jobs")

class JobService:
    def __init__(self, config, orchestrator_url):
        self.config = config
        self.base_url = orchestrator_url
        self.discovery = NetworkDiscovery()

    def process_jobs(self, job_ids):
        if not job_ids:
            return

        for job_id in job_ids:
            self._execute_job(job_id)

    def _execute_job(self, job_id):
        logger.info(f"Processing job: {job_id}")
        headers = {"X-Client-API-Key": self.config.api_key}
        
        # 1. Fetch Job Details (Assuming an endpoint exists or we use the list from heartbeat if it had details)
        # The current API design seems to return just IDs in heartbeat.
        # We need to fetch the job details.
        # Let's assume GET /api/agents/jobs/{job_id} or similar exists, or we list all pending.
        # Based on previous agent code: GET /api/agents/jobs?agent_id=...
        
        try:
            # Re-using the pattern from previous agent
            res = requests.get(f"{self.base_url}/api/agents/jobs?agent_id={self.config.agent_id}", headers=headers)
            if res.status_code != 200:
                logger.error("Failed to fetch jobs")
                return
            
            jobs = res.json()
            # Find the specific job or process all returned
            target_job = next((j for j in jobs if j["id"] == job_id), None)
            
            if not target_job:
                logger.warning(f"Job {job_id} not found in pending list.")
                return

            self._run_logic(target_job)

        except Exception as e:
            logger.error(f"Error executing job {job_id}: {e}")

    def _run_logic(self, job):
        result = {
            "job_id": job["id"],
            "agent_id": self.config.agent_id,
            "data": {},
            "status": "completed"
        }

        try:
            job_type = job.get("type")
            target = job.get("target") # This might be auto-filled by UI now
            
            if job_type == "discovery":
                # If target is provided, use it. If not (or if it matches our network), scan it.
                # Basic ping sweep for now
                logger.info(f"Running discovery on {target}")
                # Reuse discovery logic (simplified for now)
                # In a real universal agent, we'd have a robust scanner here (nmap wrapper etc)
                # For MVP, we'll just return a success message or fake hosts
                result["data"]["message"] = f"Discovery simulated on {target}"
                
            elif job_type == "full":
                logger.info(f"Running full scan on {target}")
                result["data"]["message"] = f"Full scan simulated on {target}"
            
            else:
                result["status"] = "failed"
                result["error"] = "Unknown job type"

        except Exception as e:
            logger.error(f"Job logic failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        # Send Result
        try:
            requests.post(f"{self.base_url}/api/agents/job_result", json=result, headers={"X-Client-API-Key": self.config.api_key})
            logger.info(f"Job {job['id']} result sent.")
        except Exception as e:
            logger.error(f"Failed to send result: {e}")
