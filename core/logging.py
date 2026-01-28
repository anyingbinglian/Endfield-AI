import logging
from typing import Optional


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a simple, readable format."""
    root = logging.getLogger()
    if root.handlers:
        # Already configured
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger with default configuration."""
    setup_logging()
    return logging.getLogger(name)

