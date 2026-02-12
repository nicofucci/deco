import time
import threading
import psutil
from core.logger import logger
from core.config import config_loader
from comms.client import get_api_client

class HeartbeatService:
    def __init__(self):
        self.config = config_loader.load()
        self.client = get_api_client()
        self.interval = self.config.heartbeat_interval
        self._stop_event = threading.Event()
        self._thread = None

    def _collect_metrics(self):
        """Collects basic system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "uptime": int(time.time() - psutil.boot_time())
        }

    def _loop(self):
        logger.info(f"Heartbeat loop started (Interval: {self.interval}s)")
        while not self._stop_event.is_set():
            try:
                metrics = self._collect_metrics()
                response = self.client.send_heartbeat(status="online", metrics=metrics)
                
                # Check for pending jobs in response (future implementation)
                if response.get("pending_jobs"):
                    logger.info(f"Pending jobs received: {response['pending_jobs']}")
                    
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
            
            # Wait for next interval or stop event
            if self._stop_event.wait(self.interval):
                break
        logger.info("Heartbeat loop stopped.")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
