import logging
import sys
from pathlib import Path

from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO") -> None:
    """Configure JSON + console dual logging. Call once at app startup."""
    root = logging.getLogger()
    root.setLevel(log_level.upper())

    # Remove existing handlers
    root.handlers.clear()

    # Console handler — human-readable format for local dev
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level.upper())
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # JSON file handler — structured logs for production/analysis
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setLevel(log_level.upper())
    json_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    file_handler.setFormatter(json_formatter)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Use as: logger = get_logger(__name__)"""
    return logging.getLogger(name)
