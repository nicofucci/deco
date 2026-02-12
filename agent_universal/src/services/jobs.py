import logging
import requests
import time
from .network_discovery import NetworkDiscovery

logger = logging.getLogger("DecoAgent.Jobs")


class JobService:
    def __init__(self, config, orchestrator_url):
        self.config = config
        self.base_url = orchestrator_url.rstrip("/")
        self.discovery = NetworkDiscovery()

    def process_jobs(self, job_ids):
        if not job_ids:
            return

        for job_id in job_ids:
            self._execute_job(job_id)

    def _execute_job(self, job_id):
        logger.info("Processing job: %s", job_id)
        if not self.config.api_key:
            logger.error("Cannot process job: missing API key")
            return
        headers = {"X-Client-API-Key": self.config.api_key}

        try:
            res = requests.get(
                f"{self.base_url}/api/agents/jobs",
                params={"agent_id": self.config.agent_id},
                headers=headers,
                timeout=10,
            )
            if res.status_code != 200:
                logger.error("Failed to fetch jobs: %s %s", res.status_code, res.text)
                return

            jobs = res.json()
            target_job = next((j for j in jobs if j["id"] == job_id), None)
            if not target_job:
                logger.warning("Job %s not found in pending list.", job_id)
                return

            self._run_logic(target_job)

        except Exception as e:  # pragma: no cover
            logger.error("Error executing job %s: %s", job_id, e)

    def _run_logic(self, job):
        result = {
            "job_id": job["id"],
            "agent_id": self.config.agent_id,
            "data": {},
            "status": "completed",
        }

        try:
            job_type = job.get("type")
            target = job.get("target")

            if job_type == "discovery":
                logger.info("Running discovery on %s", target)
                result["data"]["message"] = f"Discovery simulated on {target}"
            elif job_type in ("full", "ports"):
                logger.info("Running full scan on %s", target)
                result["data"]["message"] = f"Full scan simulated on {target}"
            else:
                result["status"] = "failed"
                result["error"] = "Unknown job type"

        except Exception as e:  # pragma: no cover
            logger.error("Job logic failed: %s", e)
            result["status"] = "failed"
            result["error"] = str(e)

        # Send Result
        try:
            requests.post(
                f"{self.base_url}/api/agents/job_result",
                json=result,
                headers={"X-Client-API-Key": self.config.api_key},
                timeout=10,
            )
            logger.info("Job %s result sent.", job["id"])
        except Exception as e:  # pragma: no cover
            logger.error("Failed to send result for %s: %s", job["id"], e)
