import os
import platform
import sys
from pathlib import Path

# Constants
AGENT_VERSION = "1.0.0"
ORCHESTRATOR_URL = "http://api.deco-security.com"  # Default, can be overridden
API_KEY_HEADER = "X-Client-API-Key"

IS_WINDOWS = platform.system() == "Windows"

# Valores por defecto (se pueden sobrescribir con set_config_file)
if IS_WINDOWS:
    BASE_DIR = Path(os.getenv("PROGRAMDATA", "C:\\ProgramData")) / "DecoSecurity"
    LOG_DIR = BASE_DIR / "logs"
    CONFIG_FILE = BASE_DIR / "config.json"
    BIN_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent.parent / "bin"
else:
    if os.geteuid() == 0:
        BASE_DIR = Path("/etc/deco-security")
        LOG_DIR = Path("/var/log/deco-agent")
    else:
        BASE_DIR = Path.home() / ".deco-security"
        LOG_DIR = BASE_DIR / "logs"
    CONFIG_FILE = BASE_DIR / "agent_config.json"
    BIN_DIR = Path(__file__).parent.parent / "bin"

# Ensure dirs exist
def init_dirs():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def set_config_file(custom_path: Path):
    """
    Permite sobrescribir la ruta del archivo de config (p.ej. al pasar --config en CLI).
    """
    global CONFIG_FILE
    CONFIG_FILE = Path(custom_path)
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Nmap Path
if IS_WINDOWS:
    NMAP_PATH = BIN_DIR / "nmap.exe"
else:
    NMAP_PATH = "/usr/bin/nmap" # Assume installed via package manager on Linux for now
