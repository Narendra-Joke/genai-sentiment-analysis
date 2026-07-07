import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from app.core.config import LOG_DIR

def setup_logging():
    # Ensure logs directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Timestamped log file (per run)
    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
    log_file_path = os.path.join(LOG_DIR, log_filename)

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs if setup_logging() is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Common formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s"
    )

    # Rotating File Handler (persistent logs)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5_000_000,   # 5 MB
        backupCount=5         # keep last 5 files
    )
    file_handler.setFormatter(formatter)

    # Console Handler (for debugging / dev)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging system initialized")