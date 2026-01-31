"""FastAPI dependencies."""
from __future__ import annotations

from app.db.session import get_sessionmaker


def get_db():
    sm = get_sessionmaker()
    db = sm()
    try:
        yield db
    finally:
        db.close()
