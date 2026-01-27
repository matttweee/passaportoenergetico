from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://pe:pe_password@postgres:5432/passaporto_energetico"

    STORAGE_BACKEND: str = "local"  # local | s3
    LOCAL_STORAGE_PATH: str = "/data/uploads"

    S3_ENDPOINT_URL: str | None = None
    S3_BUCKET: str = "passaporto-energetico"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_REGION: str = "eu-west-1"

    ADMIN_PASSWORD: str = "cambia-questa-password"
    SECRET_KEY: str = "cambia-questa-secret-key"

    BASE_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:3000"

    MAX_FILE_MB: int = 15
    OCR_MAX_PAGES: int = 3  # Limite pagine OCR per performance
    LOG_LEVEL: str = "INFO"
    ENV: str = "dev"  # dev | prod

    def is_production(self) -> bool:
        return self.ENV.lower() == "prod" or self.BASE_URL.startswith("https://")

    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

