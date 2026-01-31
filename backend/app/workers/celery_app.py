"""Celery app for Bollettometro 2030."""
from __future__ import annotations

from celery import Celery
from app.core.config import get_settings

settings = get_settings()

app = Celery(
    "bollettometro",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
)
