import sys
import os
import time
import socket
import servicemanager
import win32serviceutil
import win32service
import win32event

# Add src to path to allow imports when running as service/exe
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.core.lifecycle import lifecycle
from src.core.logger import logger

class DecoSecurityAgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DecoSecurityAgent"
    _svc_display_name_ = "Deco Security Agent Service"
    _svc_description_ = "Deco Security Agent for Endpoint Protection and Monitoring"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        logger.info("Service stopping...")
        win32event.SetEvent(self.hWaitStop)
        lifecycle.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logger.info("Service started.")
        self.main()

    def main(self):
        try:
            lifecycle.start()
        except Exception as e:
            logger.error(f"Service crash: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Run as console script (dev mode)
        logger.info("Running in console mode (Dev). Press Ctrl+C to stop.")
        try:
            lifecycle.start()
        except KeyboardInterrupt:
            lifecycle.stop()
            print("\nStopped.")
    else:
        # Service mode logic setup
        win32serviceutil.HandleCommandLine(DecoSecurityAgentService)
