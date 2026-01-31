"""DB session factory."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from functools import lru_cache

from app.core.config import get_settings
from app.db.base import Base
from app.db.models import *  # noqa: F401, F403


@lru_cache
def get_engine():
    return create_engine(get_settings().DATABASE_URL, pool_pre_ping=True, echo=False)


def get_sessionmaker():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Session:
    sm = get_sessionmaker()
    db = sm()
    try:
        yield db
    finally:
        db.close()
