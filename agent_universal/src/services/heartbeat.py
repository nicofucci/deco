import logging
import platform
import time
from datetime import datetime, timezone

import requests

from .network_discovery import NetworkDiscovery

logger = logging.getLogger("DecoAgent.Heartbeat")


class HeartbeatService:
    def __init__(self, config, orchestrator_url):
        self.config = config
        self.base_url = orchestrator_url.rstrip("/")
        self.discovery = NetworkDiscovery()
        self._degraded = False

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        backoff = 2
        for attempt in range(4):
            try:
                resp = requests.request(method, url, timeout=10, **kwargs)
                return resp
            except Exception as exc:
                logger.warning("Request error (attempt %s) %s: %s", attempt + 1, url, exc)
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
        return None

    def register(self):
        if self.config.agent_id:
            logger.info("Agent already registered with ID: %s", self.config.agent_id)
            return True

        if not self.config.api_key:
            logger.error("Cannot register: missing API key (set X_CLIENT_API_KEY).")
            self.config.update_state(last_error="missing_api_key")
            return False

        hostname = platform.node()
        payload = {
            "hostname": hostname,
            "version": self.config.agent_version,
            "os": platform.system(),
            "arch": platform.machine(),
        }
        headers = {"X-Client-API-Key": self.config.api_key}

        logger.info("Registering agent (host=%s, mode=%s, url=%s)...", hostname, self.config.agent_mode, self.base_url)
        res = self._request("POST", "/api/agents/register", json=payload, headers=headers)
        if not res:
            logger.error("Registration failed: no response from orchestrator.")
            self.config.update_state(last_error="register_timeout")
            return False

        if res.status_code == 201:
            data = res.json()
            self.config.set_agent_id(data.get("agent_id"))
            self.config.update_state(last_sync=datetime.now(timezone.utc).isoformat(), last_error=None)
            logger.info("Registration successful. ID: %s", data.get("agent_id"))
            self._degraded = False
            return True

        logger.error("Registration failed: %s %s", res.status_code, res.text)
        self.config.update_state(last_error=f"register_failed_{res.status_code}")
        return False

    def send_heartbeat(self):
        if not self.config.agent_id:
            logger.warning("Cannot send heartbeat: Agent not registered.")
            return None

        headers = {"X-Client-API-Key": self.config.api_key}

        network_info = self.discovery.get_network_info()
        payload = {
            "agent_id": self.config.agent_id,
            "status": "online" if not self._degraded else "degraded",
            "load_avg": 0.0,
            "memory_usage": 0.0,
            "local_ip": network_info.get("local_ip"),
            "primary_cidr": network_info.get("primary_cidr"),
            "interfaces": network_info.get("interfaces", []),
            "version": self.config.agent_version,
        }

        res = self._request("POST", "/api/agents/heartbeat", json=payload, headers=headers)
        if not res:
            logger.warning("Heartbeat timeout, entering degraded mode.")
            self._degraded = True
            self.config.update_state(last_error="heartbeat_timeout")
            return None

        if res.status_code == 200:
            data = res.json()
            logger.info(
                "Heartbeat OK status=%s pending_jobs=%s",
                data.get("status"),
                len(data.get("pending_jobs", [])),
            )
            self._degraded = False
            self.config.update_state(last_sync=datetime.now(timezone.utc).isoformat(), last_error=None)
            return data.get("pending_jobs", [])

        logger.warning("Heartbeat failed: %s %s", res.status_code, res.text)
        self._degraded = True
        self.config.update_state(last_error=f"heartbeat_failed_{res.status_code}")
        return None
