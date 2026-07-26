"""
Centralized logging module for the YOLO11 Accident Detection pipeline.

Provides a dual-output logger (console + rotating file) that can be
imported by any module in the project via:

    from src.utils.logger import log

Log files are written to <PROJECT_ROOT>/logs/ with daily rotation and
automatic cleanup of old backups.
"""

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Logger factory
# ---------------------------------------------------------------------------

def setup_logger(name: str = "yolo_project", log_level: int = logging.INFO) -> logging.Logger:
    """
    Create and return a configured logger instance.

    Features:
        - Stream handler for real-time console output.
        - RotatingFileHandler (10 MB cap, 5 backups) for persistent storage.
        - Prevents duplicate handlers on repeated calls.

    Args:
        name:      Logger namespace identifier.
        log_level: Minimum severity level (default: INFO).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(module)s:%(funcName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file output
    today_str = datetime.now().strftime("%Y%m%d")
    log_file = LOGS_DIR / f"{name}_{today_str}.log"

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# ---------------------------------------------------------------------------
# Module-level singleton used across the entire project
# ---------------------------------------------------------------------------
log = setup_logger()
