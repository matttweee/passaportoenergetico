from __future__ import annotations

import os
from pathlib import Path

from app.storage.base import Storage


class LocalStorage(Storage):
    def __init__(self, base_path: str, base_url: str):
        self.base_path = Path(base_path)
        self.base_url = base_url.rstrip("/")

    def _full_path(self, storage_path: str) -> Path:
        # storage_path è relativo (senza leading slash)
        rel = storage_path.lstrip("/").replace("\\", "/")
        return self.base_path / rel

    def save_bytes(self, data: bytes, storage_path: str, mime: str) -> str:
        full = self._full_path(storage_path)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(data)
        return storage_path

    def read_bytes(self, storage_path: str) -> bytes:
        full = self._full_path(storage_path)
        return full.read_bytes()

    def get_presigned_put_url(self, storage_path: str, mime: str, expires_seconds: int = 900) -> str:
        # "Fake presigned" per dev: PUT al backend
        return f"{self.base_url}/api/storage/local/put?path={storage_path}"

