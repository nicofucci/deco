import logging
import time
from agent.network import NetworkService
from agent.updater import UpdaterService
from agent.api import APIClient
from agent.utils import setup_logging

logger = setup_logging("DecoJobs")

class JobService:
    def __init__(self, config, api_client: APIClient):
        self.config = config
        self.api = api_client
        self.network = NetworkService()
        self.updater = UpdaterService(config, api_client)

    def process_jobs(self, job_ids):
        if not job_ids:
            return

        for job_id in job_ids:
            self._execute_job(job_id)

    def _execute_job(self, job_id):
        logger.info(f"Processing job: {job_id}")
        
        try:
            # Fetch Job Details via API
            jobs = self.api.get_jobs(self.config.agent_id)
            if not jobs:
                logger.error("Failed to fetch jobs details")
                return
            
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
            target = job.get("target")
            
            # --- JOB LOGIC ---
            
            if job_type == "scan_local_ports":
                logger.info("Running local port scan...")
                ports_to_scan = [21, 22, 23, 25, 53, 80, 443, 3389, 8080, 8443]
                open_ports = self.network.scan_ports("127.0.0.1", ports_to_scan)
                result["data"] = {
                    "open_ports": open_ports,
                    "protocol": "tcp",
                    "target": "127.0.0.1"
                }

            elif job_type in ["discovery", "discovery_network"]:
                # Use target CIDR or primary CIDR
                cidr = target if target else self.network.get_network_info().get("primary_cidr")
                if not cidr:
                    raise Exception("No CIDR available for discovery")
                
                logger.info(f"Running discovery on {cidr}...")
                active_hosts = self.network.ping_sweep(cidr)
                
                # Scan ports on active hosts
                hosts_data = []
                ports_to_scan = [22, 80, 443, 3389]
                
                for ip in active_hosts:
                    open_ports = self.network.scan_ports(ip, ports_to_scan)
                    hosts_data.append({
                        "ip": ip,
                        "open_ports": open_ports
                    })
                
                result["data"] = {
                    "cidr": cidr,
                    "hosts": hosts_data,
                    "count": len(hosts_data)
                }

            elif job_type == "full":
                # Similar to discovery but maybe deeper (simulated depth for now)
                cidr = target if target else self.network.get_network_info().get("primary_cidr")
                if not cidr:
                     raise Exception("No CIDR available for full scan")

                logger.info(f"Running full scan on {cidr}...")
                active_hosts = self.network.ping_sweep(cidr)
                
                hosts_data = []
                ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 3306, 3389, 5432, 8080, 8443]
                
                for ip in active_hosts:
                    open_ports = self.network.scan_ports(ip, ports_to_scan)
                    
                    # Enhanced Scan: Hostname & Banners
                    hostname = self.network.resolve_hostname(ip)
                    banners = {}
                    for port in open_ports:
                        banner = self.network.grab_banner(ip, port)
                        if banner:
                            banners[str(port)] = banner

                    hosts_data.append({
                        "ip": ip,
                        "hostname": hostname,
                        "open_ports": open_ports,
                        "banners": banners
                    })
                
                result["data"] = {
                    "cidr": cidr,
                    "hosts": hosts_data,
                    "count": len(hosts_data),
                    "mode": "full"
                }

            elif job_type == "agent_update":
                url = job.get("params", {}).get("url")
                version = job.get("params", {}).get("version")
                if url and version:
                    self.updater.update_agent(url, version)
                    result["data"]["message"] = "Update initiated"
                else:
                    raise Exception("Missing update params")

            else:
                # Fallback / Unknown
                logger.warning(f"Unknown job type: {job_type}")
                result["data"]["message"] = f"Job type {job_type} not implemented yet."
            
            # -----------------

        except Exception as e:
            logger.error(f"Job logic failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        # Send Result via API
        self.api.send_job_result(result)
