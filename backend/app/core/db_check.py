from __future__ import annotations

import logging
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.session import get_engine

logger = logging.getLogger(__name__)


def wait_for_db(max_retries: int = 30, delay_seconds: float = 1.0) -> bool:
    """Attende che il database sia pronto. Ritorna True se OK, False se timeout."""
    engine = get_engine()
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection OK")
            return True
        except OperationalError as e:
            if i < max_retries - 1:
                logger.warning(f"Database not ready (attempt {i+1}/{max_retries}), retrying in {delay_seconds}s...")
                time.sleep(delay_seconds)
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                return False
    return False
