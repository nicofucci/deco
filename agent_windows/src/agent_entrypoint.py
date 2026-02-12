import os
import sys
import servicemanager
import win32event
import win32service
import win32serviceutil

from pathlib import Path

# Ensure agent_universal is importable
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
UNIVERSAL_SRC = PROJECT_ROOT / "agent_universal" / "src"
if str(UNIVERSAL_SRC) not in sys.path:
    sys.path.insert(0, str(UNIVERSAL_SRC))

from main import main as universal_main  # type: ignore
from config import Config
from utils import setup_logging

logger = setup_logging("DecoService")

class DecoSecurityService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DecoSecurityAgent"
    _svc_display_name_ = "Deco-Security Agent"
    _svc_description_ = "Agente Deco-Security Universal"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        try:
            universal_main()
        except Exception as exc:  # pragma: no cover
            logger.error("Service crashed: %s", exc)
            servicemanager.LogErrorMsg(f"Service crash: {exc}")
            raise


def print_status():
    cfg = Config()
    print(f"Agent Version : {cfg.agent_version}")
    print(f"Agent Mode    : {cfg.agent_mode}")
    print(f"Agent ID      : {cfg.agent_id}")
    print(f"Orchestrator  : {cfg.orchestrator_url}")
    print(f"Last Sync     : {cfg.last_sync}")
    print(f"Last Error    : {cfg.last_error}")
    print(f"API Key       : {cfg.masked_key()}")


def print_version():
    cfg = Config()
    print(cfg.agent_version)


def print_diagnostics():
    cfg = Config()
    print_status()
    # Could be extended with service state querying if desired.


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in {"status", "version", "diagnostics"}:
            if cmd == "status":
                print_status()
            elif cmd == "version":
                print_version()
            else:
                print_diagnostics()
            return
        # Delegate service control commands to pywin32 helper
        win32serviceutil.HandleCommandLine(DecoSecurityService)
    else:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DecoSecurityService)
        servicemanager.StartServiceCtrlDispatcher()


if __name__ == "__main__":
    main()
