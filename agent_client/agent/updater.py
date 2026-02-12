import requests
import hashlib
import os
import subprocess
import sys
import time
from .config import config

class Updater:
    def __init__(self):
        self.base_url = config.orchestrator_url
        self.api_key = config.client_api_key

    def check_for_update(self, current_version, platform="windows"):
        """
        Checks if a new version is available.
        Returns metadata dict or None.
        """
        try:
            url = f"{self.base_url}/api/agents/update-metadata"
            params = {
                "platform": platform,
                "current_version": current_version,
                "agent_id": config.agent_id
            }
            # Add headers? 
            # The current backend router relies on Depends(get_db) but not strictly API Key for metadata check?
            # Let's verify router. It doesn't use `verify_api_key`.
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("update_available"):
                    return data
            return None
        except Exception as e:
            print(f"[!] Update Check Failed: {e}")
            return None

    def perform_update(self, metadata):
        """
        Downloads and runs the installer.
        """
        url = metadata["download_url"]
        expected_sha256 = metadata["sha256"]
        version = metadata["latest_version"]
        
        print(f"[*] Update Available: {version}")
        print(f"[*] Downloading from {url}...")
        
        try:
            # 1. Download
            local_filename = f"DecoAgentSetup_{version}.exe"
            if sys.platform != "win32":
                 local_filename = f"DecoAgentUpdate_{version}"

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # 2. Verify SHA256
            if not self.verify_sha256(local_filename, expected_sha256):
                print("[!] SHA256 Mismatch! Aborting update.")
                os.remove(local_filename)
                return False
                
            print("[*] Checksum Verified. Installing...")
            
            # 3. Execute Installer (Windows)
            if sys.platform == "win32": 
                # Run installer silently and restart service
                # /VERYSILENT /SUPPRESSMSGBOXES /NORESTART is typical for Inno Setup
                # If it's an MSI: msiexec /i ... /qn
                # Assuming Inno Setup based on context
                subprocess.Popen([local_filename, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/FORCECLOSEAPPLICATIONS"], shell=True)
                
                # We should exit this process to allow overwrite
                print("[*] Installer launched. Exiting agent to allow update...")
                time.sleep(2)
                sys.exit(0) 
            else:
                # Linux simple replace (MVP for Leoslo simulation)
                print("[!] Linux Auto-Update not fully implemented in this MVP script. Just pretending.")
                return True

        except Exception as e:
            print(f"[!] Update Failed: {e}")
            self.report_status(version, "failed", str(e))
            return False

    def verify_sha256(self, filepath, expected):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == expected

    def report_status(self, version, status, message=""):
        try:
            url = f"{self.base_url}/api/agents/{config.agent_id}/update-status"
            payload = {
                "previous_version": "current (TBD)", 
                "new_version": version,
                "status": status,
                "message": message
            }
            requests.post(url, json=payload)
        except:
            pass
