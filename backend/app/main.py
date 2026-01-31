"""Bollettometro 2030 - FastAPI app."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.deps import get_db
from app.api.routes import health, session, upload, analysis, result, passport, share, map as map_route, storage_serve

settings = get_settings()
setup_logging(settings.LOG_LEVEL)

app = FastAPI(title="Bollettometro 2030 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(result.router, prefix="/api")
app.include_router(passport.router, prefix="/api")
app.include_router(share.router, prefix="/api")
app.include_router(map_route.router, prefix="/api")
app.include_router(storage_serve.router, prefix="/api")

@app.get("/health")
def root_health():
    from fastapi.responses import JSONResponse
    content, status_code = health.health()
    return JSONResponse(content=content, status_code=status_code)
