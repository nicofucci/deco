import requests
import json
import logging
import os
import time

logger = logging.getLogger("ndr_sensor")

class OrchClient:
    def __init__(self):
        self.base_url = os.getenv("ORCH_URL", "http://localhost:18001")
        self.api_key = os.getenv("ORCH_API_KEY", "")
        self.spool_file = "/logs/pending_observations.jsonl"

    def ingest(self, client_id: str, observations: list):
        url = f"{self.base_url}/api/network/clients/{client_id}/observations"
        headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        
        from datetime import datetime, timezone
        now_ts = datetime.now(timezone.utc).isoformat()
        for o in observations:
            if "timestamp" not in o:
                o["timestamp"] = now_ts
                # Remove 'ts' if present to avoid confusion, or keep for legacy/debug
                # o.pop("ts", None)
        
        payload = observations # Send list directly as per requirement "Body: lista de NetworkObservation"
        
        # 1. Try to flush spool first (Best Effort)
        self._flush_spool(client_id)

        # 2. Send current payload
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code in [200, 201, 202]:
                logger.info(f"Ingest Success: {len(observations)} obs to {url}")
                return True
            else:
                logger.warning(f"Ingest Failed: {resp.status_code} - {resp.text}")
                self._spool(client_id, payload)
                return False
        except Exception as e:
            logger.error(f"Ingest Error: {e}")
            self._spool(client_id, payload)
            return False

    def _spool(self, client_id: str, observations: list):
        try:
            # We wrap it to save metadata
            data = {"client_id": client_id, "observations": observations}
            with open(self.spool_file, "a") as f:
                f.write(json.dumps(data) + "\n")
            logger.info("Payload spooled to disk.")
        except Exception as e:
            logger.error(f"Spool Error: {e}")

    def _flush_spool(self, current_client_id: str = None):
        # We accept current_client_id just to match signature if needed, but we rely on file content
        if not os.path.exists(self.spool_file):
            return

        lines = []
        try:
            with open(self.spool_file, "r") as f:
                lines = f.readlines()
        except:
            return

        if not lines:
            return

        logger.info(f"Flushing {len(lines)} spooled payloads...")
        failed_lines = []
        headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

        for line in lines:
            try:
                data = json.loads(line)
                c_id = data.get("client_id")
                obs = data.get("observations", [])
                
                # If old format (no client_id), we might skip or try to use current ONLY if provided
                if not c_id:
                     if current_client_id: 
                        c_id = current_client_id 
                        # If old format wrapped in "payload" with source?
                        # Assuming new format from now on.
                     else:
                        continue 

                url = f"{self.base_url}/api/network/clients/{c_id}/observations"
                logger.info(f"Ingesting to URL: {url}")
                # Post the list of observations directly
                resp = requests.post(url, json=obs, headers=headers, timeout=5)
                
                if resp.status_code not in [200, 201, 202]:
                    failed_lines.append(line)
            except Exception as e:
                logger.error(f"Flush error: {e}")
                failed_lines.append(line)
        
        # Rewrite failed lines back to spool
        try:
            with open(self.spool_file, "w") as f:
                f.writelines(failed_lines)
        except:
            pass
