"""Structured logging."""
from __future__ import annotations

import logging
import sys

from app.core.config import get_settings


def setup_logging(level: str = "INFO") -> None:
    settings = get_settings()
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=lvl,
        format='{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","msg":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        stream=sys.stdout,
    )
