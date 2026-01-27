from __future__ import annotations

from collections.abc import Generator

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import verify_admin_session
from app.db.session import get_sessionmaker


def get_db() -> Generator[Session, None, None]:
    SessionMaker = get_sessionmaker()
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()


def require_admin(pe_admin: str | None = Cookie(default=None)) -> None:
    settings = get_settings()
    if not pe_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non autenticato")
    key = f"{settings.SECRET_KEY}|{settings.ADMIN_PASSWORD}"
    if not verify_admin_session(key, pe_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessione non valida")

