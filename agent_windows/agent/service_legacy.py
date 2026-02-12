import os
import sys
import servicemanager
import win32serviceutil
import win32service
import win32event
import logging
from agent.utils import setup_logging
from main import run_agent as main_loop

# Setup logging specifically for the service wrapper
logger = setup_logging("DecoServiceWrapper")

class DecoSecurityService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DecoSecurityAgent"
    _svc_display_name_ = "Deco-Security Agent"
    _svc_description_ = "Agente de monitoreo y seguridad para Deco-Security Global Grid."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        logger.info("Servicio detenido.")
        # In a real scenario, we might need a way to signal main_loop to stop gracefully
        # For now, process termination is acceptable as per standard Windows Service behavior for Python scripts

    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, ''))
            logger.info("Servicio iniciado.")
            
            # Ensure working directory is correct
            os.chdir(os.path.dirname(sys.executable))
            
            self.main()
        except Exception as e:
            logger.error(f"SvcDoRun Crash: {e}")
            servicemanager.LogErrorMsg(f"Service Crash: {e}")
            self.SvcStop()

    def main(self):
        try:
            logger.info("Iniciando loop principal del agente...")
            main_loop() 
        except Exception as e:
            logger.error(f"Error fatal en el servicio: {e}")
            self.SvcStop()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DecoSecurityService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DecoSecurityService)
