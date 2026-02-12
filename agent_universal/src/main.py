import logging
import subprocess
import sys
import time
from typing import Optional

import requests

from config import Config
from services.heartbeat import HeartbeatService
from services.jobs import JobService
from services.logging_utils import setup_logging

logger = logging.getLogger("DecoAgent.Main")


def _ping_orchestrator(config: Config) -> tuple[bool, Optional[str]]:
    url = f"{config.orchestrator_url.rstrip('/')}/health"
    try:
        res = requests.get(url, timeout=5)
        return res.status_code == 200, f"{res.status_code}: {res.text}"
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


def _print_status(config: Config):
    ok, detail = _ping_orchestrator(config)
    service_state = "unknown"
    if config.os_type != "Windows":
        try:
            out = subprocess.check_output(["systemctl", "is-active", "deco-security-agent"], text=True).strip()
            service_state = out
        except Exception:
            service_state = "not-installed"

    print("Deco-Security Agent Status")
    print("---------------------------")
    print(f"Orchestrator URL : {config.orchestrator_url}")
    print(f"Agent Mode       : {config.agent_mode}")
    print(f"Agent Version    : {config.agent_version}")
    print(f"Agent ID         : {config.agent_id or 'not-registered'}")
    print(f"API Key          : {config.masked_key()}")
    print(f"Last Sync        : {config.last_sync}")
    print(f"Last Error       : {config.last_error}")
    print(f"Service state    : {service_state}")
    print(f"Connectivity     : {'ok' if ok else 'fail'} ({detail})")


def _interactive_api_key(config: Config):
    print("\n" + "=" * 40)
    print(" DECO-SECURITY AGENT SETUP")
    print("=" * 40)
    print("Introduce tu API Key de Cliente (X-Client-API-Key).")
    try:
        key = input("API Key: ").strip()
    except EOFError:
        key = ""
    if key:
        config.set_api_key(key)
        logger.info("API Key stored.")
        return True
    logger.error("API Key is required. Exiting.")
    return False


def main():
    logger = setup_logging()
    config = Config()
    logger.info("Deco-Security Universal Agent Starting...")
    logger.info("Agent version: %s", config.agent_version)
    logger.info("Orchestrator base URL: %s", config.orchestrator_url)

    if len(sys.argv) > 1 and sys.argv[1].lower() == "status":
        _print_status(config)
        return

    if not config.api_key:
        if not _interactive_api_key(config):
            sys.exit(1)

    heartbeat = HeartbeatService(config, config.orchestrator_url)
    jobs = JobService(config, config.orchestrator_url)

    backoff = 5
    logger.info("Entering main loop...")
    while True:
        try:
            if not config.agent_id:
                if heartbeat.register():
                    backoff = 5
                else:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 60)
                    continue

            pending_jobs = heartbeat.send_heartbeat()
            if pending_jobs is None:
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue

            backoff = 5
            if pending_jobs:
                jobs.process_jobs(pending_jobs)

            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Stopping agent...")
            break
        except Exception as exc:  # pragma: no cover
            logger.error("Unexpected error in main loop: %s", exc)
            time.sleep(10)


if __name__ == "__main__":
    main()
