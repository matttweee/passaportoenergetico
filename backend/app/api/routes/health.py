"""Health check."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    checks = {}
    all_ok = True
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = str(e)[:100]
        all_ok = False
    try:
        from redis import Redis
        r = Redis.from_url(get_settings().REDIS_URL)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = str(e)[:100]
        all_ok = False
    status = 200 if all_ok else 503
    return {"ok": all_ok, "checks": checks}, status
