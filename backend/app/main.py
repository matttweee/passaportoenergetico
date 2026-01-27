from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_admin import router as admin_router
from app.api.routes_public import router as public_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.rate_limit import rate_limit_middleware


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)

    app = FastAPI(title="Passaporto Energetico API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting middleware (prima dei router)
    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        return await rate_limit_middleware(request, call_next)

    app.include_router(public_router, prefix="/api", tags=["public"])
    app.include_router(admin_router, prefix="/api")

    @app.get("/health")
    def health():
        from sqlalchemy import text
        from app.db.session import get_engine
        from app.storage import get_storage
        from pathlib import Path

        checks: dict[str, str] = {}
        all_ok = True

        # DB check
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)[:100]}"
            all_ok = False

        # Storage check
        try:
            storage = get_storage()
            if settings.STORAGE_BACKEND == "local":
                path = Path(settings.LOCAL_STORAGE_PATH)
                if path.exists() and path.is_dir():
                    # Test write
                    test_file = path / ".health_check"
                    test_file.write_text("ok")
                    test_file.unlink()
                    checks["storage"] = "ok"
                else:
                    checks["storage"] = "path not writable"
                    all_ok = False
            else:
                # S3: best-effort (non facciamo chiamata reale per non rallentare)
                checks["storage"] = "s3 (not tested)"
        except Exception as e:
            checks["storage"] = f"error: {str(e)[:100]}"
            all_ok = False

        status_code = 200 if all_ok else 503
        return {"ok": all_ok, "checks": checks}, status_code

    # Cleanup job (periodico, ogni ora) - solo se non in test
    if settings.ENV.lower() != "test":
        import threading
        import time as time_module

        def cleanup_job():
            """Job background per cleanup file orfani."""
            while True:
                try:
                    time_module.sleep(3600)  # 1 ora
                    from app.db.session import get_sessionmaker
                    from app.services.cleanup import cleanup_orphaned_submissions
                    SessionMaker = get_sessionmaker()
                    db = SessionMaker()
                    try:
                        cleanup_orphaned_submissions(db, older_than_hours=24)
                    finally:
                        db.close()
                except Exception as e:
                    logger.exception("cleanup_job_error")

        cleanup_thread = threading.Thread(target=cleanup_job, daemon=True)
        cleanup_thread.start()
        logger.info("Cleanup job started (runs every hour)")

    return app

    return app


app = create_app()

