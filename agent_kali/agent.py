import time
import json
import os
import sys
import platform
from typing import Dict, Any

from comm.client import DecoClient
from scanners.nmap_runner import NmapRunner

CONFIG_FILE = "config.json"
LOG_FILE = "logs/agent.log"

class DecoAgent:
    def __init__(self):
        self.config = self._load_config()
        self.client = DecoClient(
            orchestrator_url=self.config.get("orchestrator_url", "http://127.0.0.1:19001"),
            api_key=self.config.get("client_api_key")
        )
        self.agent_id = self.config.get("agent_id")
        self.scanner = NmapRunner()
        self.running = True

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def _save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)

    def _log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")

    def register(self):
        if self.agent_id:
            self._log(f"Agent already registered with ID: {self.agent_id}")
            return

        self._log("Registering agent...")
        # Si no tenemos API Key, pedimos (en modo interactivo) o fallamos
        if not self.client.api_key:
            # Fallback para pruebas automatizadas: leer de ENV
            env_key = os.environ.get("DECO_CLIENT_API_KEY")
            if env_key:
                self.client.set_api_key(env_key)
                self.config["client_api_key"] = env_key
            else:
                self._log("CRITICAL: No Client API Key found in config or environment.")
                sys.exit(1)

        hostname = platform.node()
        os_info = f"{platform.system()} {platform.release()}"
        
        resp = self.client.register_agent(hostname, "1.0.0", os_info)
        if resp and "agent_id" in resp:
            self.agent_id = resp["agent_id"]
            self.config["agent_id"] = self.agent_id
            self._save_config()
            self._log(f"Agent registered successfully. ID: {self.agent_id}")
        else:
            self._log("Failed to register agent.")
            sys.exit(1)

    def run(self):
        self._log("Starting Deco-Agent loop...")
        self.register()

        while self.running:
            try:
                # 1. Heartbeat
                hb_resp = self.client.send_heartbeat(self.agent_id)
                if not hb_resp:
                    self._log("Heartbeat failed. Retrying in 10s...")
                    time.sleep(10)
                    continue

                pending_jobs = hb_resp.get("pending_jobs", [])
                if pending_jobs:
                    self._log(f"Received {len(pending_jobs)} pending jobs.")
                    
                    for job_id in pending_jobs:
                        self._process_job(job_id)
                else:
                    # Idle
                    pass

            except KeyboardInterrupt:
                self._log("Agent stopping...")
                self.running = False
            except Exception as e:
                self._log(f"Unexpected error in main loop: {e}")
            
            time.sleep(10)

    def _process_job(self, job_id: str):
        self._log(f"Processing Job ID: {job_id}")
        
        # 1. Obtener detalles del job
        # Como no tenemos endpoint directo GET /jobs/{id} para el agente en la spec original,
        # y el cliente.py lo simula listando todos, usamos eso.
        job = self.client.get_job_details(job_id)
        if not job:
            self._log(f"Could not fetch details for job {job_id}. Skipping.")
            return

        target = job.get("target")
        job_type = job.get("type", "discovery")
        
        self._log(f"Starting scan: {job_type} on {target}")
        
        # 2. Ejecutar Scan
        scan_result = self.scanner.run_scan(target, job_type)
        
        if "error" in scan_result:
            self._log(f"Scan failed: {scan_result['error']}")
            # Podríamos subir un resultado de error
            return

        # 3. Subir Resultados
        summary = {
            "status": "OK",
            "hosts_found": len(scan_result.get("hosts", []))
        }
        
        # Asegurar que raw_data tenga lo necesario para el parser del backend
        # El backend espera 'tool', 'target', 'open_ports' (opcional)
        # Nuestro parser local ya estructura esto.
        
        success = self.client.upload_result(job_id, self.agent_id, scan_result, summary)
        if success:
            self._log(f"Result uploaded successfully for Job {job_id}")
        else:
            self._log(f"Failed to upload result for Job {job_id}")

if __name__ == "__main__":
    agent = DecoAgent()
    agent.run()
