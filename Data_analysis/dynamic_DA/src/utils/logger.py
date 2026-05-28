"""
Logger Utility
==============
Centralized, colored, file-and-console logging for the pipeline.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from colorama import Fore, Style, init

# Initialise colorama for cross-platform color support
init(autoreset=True)

# Lazy import of settings to avoid circular imports
def _get_log_settings():
    from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT
    return LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


class ColorFormatter(logging.Formatter):
    """Custom formatter that adds colors to console log output."""

    COLORS = {
        logging.DEBUG:    Fore.CYAN,
        logging.INFO:     Fore.GREEN,
        logging.WARNING:  Fore.YELLOW,
        logging.ERROR:    Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname:<8}{Style.RESET_ALL}"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured with both console (colored)
    and rotating file handlers.

    Args:
        name: Module/component name used as the logger identifier.

    Returns:
        Configured logging.Logger instance.
    """
    LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT = _get_log_settings()

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # ── Console Handler (colored) ──────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        ColorFormatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    )
    console_handler.setLevel(logging.DEBUG)

    # ── File Handler (plain text) ──────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"pipeline_{timestamp}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    )
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
