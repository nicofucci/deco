import os
import sys
import logging
import subprocess
from agent.api import APIClient
from agent.utils import setup_logging

logger = setup_logging("DecoUpdater")

class UpdaterService:
    def __init__(self, config, api_client: APIClient):
        self.config = config
        self.api = api_client

    def update_agent(self, download_url: str, version: str):
        """
        Descarga el nuevo binario y programa su ejecución.
        """
        logger.info(f"Starting update to version {version} from {download_url}")
        
        try:
            current_exe = sys.executable
            new_exe = current_exe + ".new"
            
            # 1. Download new exe using API client
            if not self.api.download_file(download_url, new_exe):
                logger.error("Download failed.")
                return False
                    
            logger.info("Download completed.")
            
            # 2. Create update script (batch)
            batch_script = f"""
@echo off
timeout /t 5 /nobreak > NUL
:loop
tasklist | find "{os.path.basename(current_exe)}" > NUL
if not errorlevel 1 (
    timeout /t 1 > NUL
    goto loop
)
move /y "{new_exe}" "{current_exe}"
net start DecoSecurityAgent
del "%~f0"
"""
            script_path = os.path.join(os.path.dirname(current_exe), "update_agent.bat")
            with open(script_path, "w") as f:
                f.write(batch_script)
                
            logger.info("Update script created. Exiting to apply update.")
            
            # 3. Execute script and exit
            subprocess.Popen([script_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit(0) # Exit to allow replacement
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False
