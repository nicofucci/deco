import json
import logging
import os
import platform
import shutil
import time
from pathlib import Path

logger = logging.getLogger("DecoConfig")

DEFAULT_ORCHESTRATOR_URL = "http://127.0.0.1:8001"
DEFAULT_AGENT_MODE = os.environ.get("AGENT_MODE", "prod")
DEFAULT_AGENT_VERSION = os.environ.get("AGENT_VERSION", "2.0.0-universal")


class Config:
    """
    Config manager with env overrides, atomic writes, and rollback support.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.config_path = self._get_config_path()
        self._data = self._default_data()
        self.load()

    # ---- Properties -----------------------------------------------------
    @property
    def orchestrator_url(self) -> str:
        return self._data.get("orchestrator_url") or DEFAULT_ORCHESTRATOR_URL

    @property
    def api_key(self) -> str | None:
        return self._data.get("api_key")

    @property
    def agent_id(self) -> str | None:
        return self._data.get("agent_id")

    @property
    def agent_mode(self) -> str:
        return self._data.get("agent_mode", DEFAULT_AGENT_MODE)

    @property
    def agent_version(self) -> str:
        return self._data.get("agent_version", DEFAULT_AGENT_VERSION)

    @property
    def last_sync(self):
        return self._data.get("last_sync")

    @property
    def last_error(self):
        return self._data.get("last_error")

    # ---- Load / Save ----------------------------------------------------
    def _get_config_path(self) -> Path:
        if self.os_type == "Windows":
            program_data = os.environ.get("ProgramData", "C:\\ProgramData")
            return Path(program_data) / "DecoSecurityAgent" / "config.json"

        etc_path = Path("/etc/deco-security-agent/config.json")
        if etc_path.exists():
            return etc_path
        # Fallback to repo-local for dev/test
        return Path(__file__).resolve().parent.parent / "config.json"

    def _default_data(self) -> dict:
        return {
            "orchestrator_url": os.environ.get("DECO_ORCHESTRATOR_URL", DEFAULT_ORCHESTRATOR_URL),
            "api_key": os.environ.get("X_CLIENT_API_KEY") or os.environ.get("DECO_CLIENT_API_KEY"),
            "agent_id": os.environ.get("AGENT_ID"),
            "agent_mode": DEFAULT_AGENT_MODE,
            "agent_version": DEFAULT_AGENT_VERSION,
            "last_sync": None,
            "last_error": None,
        }

    def load(self):
        if self.config_path.exists():
            try:
                with self.config_path.open("r") as fh:
                    data = json.load(fh)
                    if isinstance(data, dict):
                        # Merge with defaults to keep new keys
                        merged = {**self._default_data(), **data}
                        self._data = merged
            except Exception as exc:  # pragma: no cover
                logger.error("Error loading config: %s", exc)

        # Validate minimum fields
        if not self._data.get("orchestrator_url"):
            self._data["orchestrator_url"] = DEFAULT_ORCHESTRATOR_URL
        if not self._data.get("agent_mode"):
            self._data["agent_mode"] = DEFAULT_AGENT_MODE
        if not self._data.get("agent_version"):
            self._data["agent_version"] = DEFAULT_AGENT_VERSION

    def save(self):
        """
        Atomic write with backup to avoid corruption.
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.config_path.with_suffix(".tmp")
            with temp_path.open("w") as fh:
                json.dump(self._data, fh, indent=2)
            os.replace(temp_path, self.config_path)
        except Exception as exc:  # pragma: no cover
            logger.error("Error saving config: %s", exc)

    def backup(self):
        try:
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix(f".bak.{int(time.time())}")
                shutil.copy2(self.config_path, backup_path)
                return backup_path
        except Exception as exc:  # pragma: no cover
            logger.error("Error creating config backup: %s", exc)
        return None

    def set_api_key(self, key: str | None):
        self._data["api_key"] = key
        self.save()

    def set_agent_id(self, agent_id: str | None):
        self._data["agent_id"] = agent_id
        self.save()

    def update_state(self, last_sync=None, last_error=None):
        if last_sync is not None:
            self._data["last_sync"] = last_sync
        if last_error is not None:
            self._data["last_error"] = last_error
        self.save()

    def masked_key(self) -> str:
        """
        Return partially masked API key for logs.
        """
        key = self.api_key or ""
        if len(key) <= 6:
            return "***"
        return f"{key[:3]}***{key[-3:]}"
