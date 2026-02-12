import logging
import os
from logging.handlers import RotatingFileHandler
from ..config import config

def setup_logger():
    """Configures the application logger."""
    os.makedirs(config.log_path, exist_ok=True)
    log_file = os.path.join(config.log_path, "agent.log")

    logger = logging.getLogger("DecoAgent")
    logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler (for dev/debug)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
