import os
import logging
import sys
import tempfile
from logging.handlers import RotatingFileHandler

def setup_logging(name="DecoAgent", log_level=logging.INFO):
    """
    Configura un sistema de logging robusto que intenta escribir en ProgramData,
    pero hace fallback a Temp si falla por permisos.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handlers = []

    # 1. Console Handler (siempre útil para debug manual)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # 2. File Handler (ProgramData)
    try:
        # Detectar OS y ruta adecuada
        if os.name == 'nt':
            program_data = os.environ.get("ProgramData", "C:\\ProgramData")
            log_dir = os.path.join(program_data, "DecoSecurity", "logs")
        else:
            log_dir = "/var/log/deco-security" # Linux fallback
            
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "agent.log")
        
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
        
    except Exception as e:
        # 3. Fallback a Temp
        try:
            temp_dir = tempfile.gettempdir()
            log_file = os.path.join(temp_dir, "DecoSecurity_fallback.log")
            fallback_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
            fallback_handler.setFormatter(formatter)
            handlers.append(fallback_handler)
            # Loguear el error original en el fallback
            logger.warning(f"No se pudo escribir en log principal: {e}. Usando fallback: {log_file}")
        except Exception:
            pass

    for h in handlers:
        logger.addHandler(h)

    return logger
