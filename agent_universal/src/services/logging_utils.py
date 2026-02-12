import json
import logging
import os
import platform
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _build_formatter():
    json_mode = os.getenv("DECO_LOG_JSON", "0") == "1"

    if not json_mode:
        return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            payload = {
                "ts": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
            }
            return json.dumps(payload)

    return JsonFormatter()


def _log_dir():
    if platform.system() == "Windows":
        program_data = os.environ.get("ProgramData", "C:\\ProgramData")
        return Path(program_data) / "DecoSecurityAgent" / "logs"

    default_dir = Path("/var/log/deco-security-agent")
    if default_dir.parent.exists() and os.access(default_dir.parent, os.W_OK):
        return default_dir
    # Fallback to repo-local logs
    return Path(__file__).resolve().parent.parent / "logs"


def setup_logging(name: str = "DecoAgent"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = _build_formatter()

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler (rotating)
    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "agent.log"

    fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
