import os
import sys
import hashlib
import requests
import time
import subprocess
import logging
import json
from ..config import config
from ..core.logger import logger
from ..core.api import api_client

# Helper to verify SHA256 (reused)
def verify_hash(path: str, expected_hash: str) -> bool:
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash

def check_for_update() -> dict:
    """Queries the backend for update metadata."""
    if not config.auto_update_enabled:
        return {}
    
    # ... same logic as before, just ensuring we use the updated file ...
    endpoint = f"{config.api_url}/api/agents/update-metadata"
    headers = {"X-Client-API-Key": config.api_key}
    params = {
        "platform": "windows",
        "current_version": config.version,
        "agent_id": config.agent_id
    }
    
    try:
        resp = requests.get(endpoint, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("update_available"):
                return data
    except Exception as e:
        logger.error(f"Failed to check for updates: {e}")
        
    return {}

def create_update_helper(dir_path: str, service_name: str = "DecoSecurityAgent"):
    """Creates the batch script to handle swap and rollback."""
    script_path = os.path.join(dir_path, "update_helper.bat")
    content = f"""@echo off
set SERVICE={service_name}
set DIR=%~dp0
set LOG=%DIR%update.log

echo [%date% %time%] Watchdog started. Stopping service for update... >> %LOG%
sc stop %SERVICE%
timeout /t 5 /nobreak

echo [%date% %time%] Swapping binaries... >> %LOG%
if exist "%DIR%DecoAgent.old" del /f /q "%DIR%DecoAgent.old"
move /y "%DIR%DecoAgent.exe" "%DIR%DecoAgent.old"
move /y "%DIR%DecoAgent.new" "%DIR%DecoAgent.exe"

echo [%date% %time%] Starting service... >> %LOG%
sc start %SERVICE%

echo [%date% %time%] Verifying startup (30s watchdog)... >> %LOG%
timeout /t 10 /nobreak
sc query %SERVICE% | find "RUNNING"
if %errorlevel% neq 0 goto ROLLBACK

timeout /t 10 /nobreak
sc query %SERVICE% | find "RUNNING"
if %errorlevel% neq 0 goto ROLLBACK

timeout /t 10 /nobreak
sc query %SERVICE% | find "RUNNING"
if %errorlevel% neq 0 goto ROLLBACK

echo [%date% %time%] Update verified stable (30s). Exiting. >> %LOG%
exit 0

:ROLLBACK
echo [%date% %time%] UPDATE FAILED/CRASHED. ROLLING BACK... >> %LOG%
sc stop %SERVICE%
timeout /t 5 /nobreak
move /y "%DIR%DecoAgent.old" "%DIR%DecoAgent.exe"
sc start %SERVICE%
echo [%date% %time%] Rollback complete. Service restored. >> %LOG%
exit 1
"""
    with open(script_path, "w") as f:
        f.write(content)
    return script_path

def perform_update(metadata: dict) -> bool:
    """Downloads and orchestrates the update via helper."""
    download_url = metadata.get("download_url")
    expected_hash = metadata.get("sha256")
    new_version = metadata.get("latest_version")
    
    logger.info(f"Starting update process to v{new_version}...")
    api_client.send_event("update_started", {"target_version": new_version})
    
    current_exe = sys.executable
    if not getattr(sys, 'frozen', False):
        logger.warning("Auto-update only works in frozen mode.")
        return False
        
    dir_name = os.path.dirname(current_exe)
    new_exe_name = "DecoAgent.new"
    new_exe_path = os.path.join(dir_name, new_exe_name)
    
    # 1. Download
    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(new_exe_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        api_client.send_event("update_failed", {"reason": "download_error", "error": str(e)})
        return False

    # 2. Verify
    if not verify_hash(new_exe_path, expected_hash):
        logger.error("Hash check failed.")
        api_client.send_event("update_failed", {"reason": "hash_mismatch"})
        os.remove(new_exe_path)
        return False

    # 3. Persist State
    state_file = os.path.join(dir_name, "update_state.json")
    with open(state_file, "w") as f:
        json.dump({"status": "pending", "target_version": new_version}, f)

    # 4. Trigger Helper
    try:
        helper_path = create_update_helper(dir_name)
        logger.info("Triggering update_helper.bat...")
        subprocess.Popen(helper_path, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS)
        sys.exit(0) # Die to allow swap
        
    except Exception as e:
        logger.error(f"Failed to trigger helper: {e}")
        return False
