from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine():
    settings = get_settings()
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def reset_engine_cache() -> None:
    get_engine.cache_clear()


def get_sessionmaker():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


__all__ = ["get_engine", "reset_engine_cache", "get_sessionmaker"]

