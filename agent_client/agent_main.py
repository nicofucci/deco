import time
import logging
import sys
import platform
import argparse
import traceback
from pathlib import Path
from modules.agent_id import AgentIdentity
from modules.heartbeat import Heartbeat
from modules.discovery import NetworkDiscovery
from modules.ports import PortScanner
from modules.http_client import HTTPClient
from modules.secure_storage import SecureStorage
from updater import Updater
from config import LOG_DIR, init_dirs, set_config_file

# Setup Logging
init_dirs()
logging.basicConfig(
    filename=LOG_DIR / "agent.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DecoAgent")

FATAL_LOG = LOG_DIR / "agent_fatal.log"


def write_fatal_log(exc: BaseException):
    """
    Escribe el traceback completo en un log separado para diagnósticos.
    """
    try:
        with open(FATAL_LOG, "a", encoding="utf-8") as f:
            f.write("\n\n=== FATAL ERROR ===\n")
            f.write(traceback.format_exc())
    except Exception:
        # Evitamos que falle el logger en cascada
        pass


class DecoAgent:
    def __init__(self, once: bool = False):
        self.identity = AgentIdentity()
        self.heartbeat = Heartbeat()
        self.discovery = NetworkDiscovery()
        self.scanner = PortScanner()
        self.client = HTTPClient()
        self.updater = Updater()
        self.once = once
        self.running = True

    def run(self):
        logger.info("Deco-Security Agent Starting...")
        
        # 1. Registration
        if not self.identity.register():
            logger.error("Registration failed. Retrying in 60s...")
            time.sleep(60)
            return

        logger.info("Agent registered/verified. Entering main loop.")

        # 2. Main Loop
        while self.running:
            try:
                # Heartbeat
                self.heartbeat.send()
                
                # Check for Jobs
                self.check_jobs()
                
                # Check for Updates
                self.updater.check_for_updates()
                
                if self.once:
                    logger.info("Modo --once activado, saliendo tras un ciclo.")
                    break

                time.sleep(20) # Loop interval
            except KeyboardInterrupt:
                logger.info("Stopping agent...")
                self.running = False
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(10)

    def check_jobs(self):
        agent_id = self.identity.get_id()
        if not agent_id:
            return

        jobs = self.client.get(f"/api/agents/jobs?agent_id={agent_id}")
        if jobs and isinstance(jobs, list):
            for job in jobs:
                self.execute_job(job)

    def execute_job(self, job):
        logger.info(f"Executing job: {job.get('id')} - {job.get('type')}")
        result = {"job_id": job.get("id"), "agent_id": self.identity.get_id(), "data": {}, "status": "failed"}
        
        try:
            job_type = job.get("type")
            target = job.get("params", {}).get("target") or job.get("target")

            if job_type in ["discovery", "discovery_basic"]:
                hosts = self.discovery.scan_network(target)
                result["data"]["hosts"] = [{"ip": ip} for ip in hosts]
                result["status"] = "completed"

            elif job_type in ["ports", "full", "scan_ports"]:
                if not target:
                    raise ValueError("No target specified")

                if "/" in target:
                    # Red: discovery + ports por host
                    hosts = self.discovery.scan_network(target)
                    enriched = []
                    for ip in hosts:
                        open_ports = self.scanner.scan_host(ip)
                        enriched.append({"ip": ip, "open_ports": open_ports})
                    result["data"]["hosts"] = enriched
                else:
                    # Host individual
                    ports = self.scanner.scan_host(target)
                    result["data"]["hosts"] = [{"ip": target, "open_ports": ports}]
                result["status"] = "completed"

            else:
                result["status"] = "failed"
                result["error"] = f"Unknown job type: {job_type}"

        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        # Send Result
        self.client.post("/api/agents/job_result", result)

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Deco-Security Agent")
    parser.add_argument("--api-key", help="Client API Key para registro rápido")
    parser.add_argument("--url", help="Orchestrator URL")
    parser.add_argument("--once", action="store_true", help="Ejecuta un solo ciclo (heartbeat + jobs) y termina")
    parser.add_argument("--config", help="Ruta custom de config.json")
    args = parser.parse_args()

    try:
        if args.config:
            set_config_file(Path(args.config))
            init_dirs()

        if args.api_key:
            storage = SecureStorage()
            storage.set("client_api_key", args.api_key)
            if args.url:
                storage.set("orchestrator_url", args.url)
            print("Configuration stored.")
            return

        agent = DecoAgent(once=args.once)
        agent.run()
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Excepción fatal: {e}")
        write_fatal_log(e)
        # Mensaje mínimo para usuario final
        print("Se produjo un error fatal. Revisa el log agent_fatal.log para más detalles.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
