"""Bollettometro 2030 - Core config."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://pe:pe_password@postgres:5432/bollettometro"
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"

    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "/data/uploads"
    S3_ENDPOINT_URL: str | None = None
    S3_BUCKET: str = "bollettometro"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_REGION: str = "eu-west-1"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    SECRET_KEY: str = "change-this-secret-key-min-32-chars"
    BASE_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:3000"

    TREND_GREEN_THRESHOLD_PCT: float = 15.0
    TREND_YELLOW_THRESHOLD_PCT: float = 30.0
    UPLOAD_TTL_HOURS: int = 24
    MAX_FILE_MB: int = 15
    LOG_LEVEL: str = "INFO"
    ENV: str = "dev"

    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
