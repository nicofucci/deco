import logging
import os
import platform
from logging.handlers import RotatingFileHandler

def setup_logging(name="DecoAgent"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    log_dir = "logs"
    if platform.system() == "Windows":
        program_data = os.environ.get("ProgramData", "C:\\ProgramData")
        log_dir = os.path.join(program_data, "DecoSecurityAgent", "logs")
    else:
        log_dir = "/var/log/deco-security-agent"
        if not os.access("/var/log", os.W_OK):
             log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "agent.log")

    fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
