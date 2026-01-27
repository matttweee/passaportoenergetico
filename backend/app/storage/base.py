from __future__ import annotations

from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save_bytes(self, data: bytes, storage_path: str, mime: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def read_bytes(self, storage_path: str) -> bytes:
        raise NotImplementedError

    def get_presigned_put_url(self, storage_path: str, mime: str, expires_seconds: int = 900) -> str | None:
        return None

