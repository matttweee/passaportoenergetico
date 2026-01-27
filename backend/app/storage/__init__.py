from __future__ import annotations

from app.core.config import get_settings
from app.storage.base import Storage
from app.storage.local import LocalStorage
from app.storage.s3 import S3Storage


def get_storage() -> Storage:
    s = get_settings()
    if s.STORAGE_BACKEND.lower() == "s3":
        return S3Storage(
            bucket=s.S3_BUCKET,
            region=s.S3_REGION,
            access_key=s.S3_ACCESS_KEY,
            secret_key=s.S3_SECRET_KEY,
            endpoint_url=s.S3_ENDPOINT_URL,
        )
    return LocalStorage(base_path=s.LOCAL_STORAGE_PATH, base_url=s.BASE_URL)

