import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import settings


_configured = False


def _configure_root_once() -> None:
    global _configured
    if _configured:
        return

    log_folder = Path(settings.log_folder)
    log_folder.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("ai_software")
    root.setLevel(settings.log_level.upper())
    root.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        filename=log_folder / "application.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_root_once()
    return logging.getLogger(f"ai_software.{name}")


# Backwards-compatible top-level logger
logger = get_logger("app")
