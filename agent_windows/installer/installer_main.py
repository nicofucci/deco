import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import win32service
import win32serviceutil

# Installer constants
PROGRAM_DATA = Path(os.environ.get("ProgramData", r"C:\\ProgramData"))
INSTALL_ROOT = PROGRAM_DATA / "DecoSecurity" / "agent"
CONFIG_FILE = INSTALL_ROOT / "config.json"
LOG_DIR = INSTALL_ROOT / "logs"
SERVICE_NAME = "DecoSecurityAgent"
SERVICE_DISPLAY = "Deco-Security Agent"
SERVICE_DESCRIPTION = "Agente Deco-Security"

DEFAULT_ORCH = "http://127.0.0.1:8001"
DEFAULT_MODE = os.environ.get("AGENT_MODE", "prod")
DEFAULT_VERSION = os.environ.get("AGENT_VERSION", "2.0.0-universal")


def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        is_admin = False
    if not is_admin:
        sys.stderr.write("ERROR: Run installer as Administrator.\n")
        sys.exit(2)


def write_config(orch_url: str, api_key: str):
    INSTALL_ROOT.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "orchestrator_url": orch_url,
        "api_key": api_key,
        "agent_id": None,
        "agent_mode": DEFAULT_MODE,
        "agent_version": DEFAULT_VERSION,
        "last_sync": None,
        "last_error": None,
    }
    if CONFIG_FILE.exists():
        try:
            existing = json.loads(CONFIG_FILE.read_text())
            if isinstance(existing, dict):
                data.update({k: v for k, v in existing.items() if v})
        except Exception:
            pass
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, CONFIG_FILE)


def copy_agent_exe():
    current_exe = Path(sys.executable)
    target = INSTALL_ROOT / "agent.exe"
    shutil.copyfile(current_exe, target)
    return target


def install_service(agent_exe: Path, orch_url: str):
    # Use the agent exe CLI to register service via win32serviceutil.HandleCommandLine
    cmd = [str(agent_exe), "--startup", "auto", "install"]
    subprocess.check_call(cmd)

    # Delayed auto start
    hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
    hs = win32service.OpenService(hscm, SERVICE_NAME, win32service.SERVICE_ALL_ACCESS)
    try:
        win32service.ChangeServiceConfig2(hs, win32service.SERVICE_CONFIG_DELAYED_AUTO_START, True)
    finally:
        win32service.CloseServiceHandle(hs)
        win32service.CloseServiceHandle(hscm)

    # Start service
    subprocess.check_call([str(agent_exe), "start"])


def wait_for_heartbeat(timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            data = json.loads(CONFIG_FILE.read_text())
            if data.get("agent_id") and data.get("last_sync"):
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def main():
    ensure_admin()

    orch_url = os.environ.get("DECO_ORCHESTRATOR_URL", DEFAULT_ORCH)
    api_key = os.environ.get("X_CLIENT_API_KEY") or os.environ.get("DECO_CLIENT_API_KEY")

    if not api_key:
        print("\n" + "="*60)
        print("  DECO SECURITY AGENT - SETUP")
        print("="*60 + "\n")
        print(f"Orchestrator URL: {orch_url}")
        print("Note: Environment variable X_CLIENT_API_KEY not found.")
        print("Please enter your Client API Key manually.\n")
        
        while not api_key:
            try:
                api_key = input("Enter X_CLIENT_API_KEY > ").strip()
                if not api_key:
                    print("Error: API Key cannot be empty. Try again.")
            except EOFError:
                sys.stderr.write("\nERROR: Input stream closed. Cannot read API Key.\n")
                sys.exit(3)
        print("\n")

    print("[Installer] Deco-Security Agent Installer")
    print(f"[Installer] Orchestrator URL: {orch_url}")

    write_config(orch_url, api_key)
    agent_exe = copy_agent_exe()

    print("[Installer] Installing Windows service...")
    install_service(agent_exe, orch_url)

    print("[Installer] Waiting for first heartbeat (30s)...")
    if not wait_for_heartbeat(timeout=30):
        sys.stderr.write("ERROR: heartbeat not observed within 30s. Check service logs.\n")
        sys.exit(4)

    print("[Installer] Agent installed and heartbeat confirmed.")
    sys.exit(0)


if __name__ == "__main__":
    if os.name != "nt":
        sys.stderr.write("ERROR: Windows-only installer.\n")
        sys.exit(1)
    main()
