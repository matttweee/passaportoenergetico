"""File storage: local or S3."""
from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO

from app.core.config import get_settings


def get_storage_path(relative: str) -> Path:
    settings = get_settings()
    base = Path(settings.LOCAL_STORAGE_PATH)
    base.mkdir(parents=True, exist_ok=True)
    full = (base / relative).resolve()
    if not str(full).startswith(str(base.resolve())):
        raise ValueError("Path escape")
    return full


def save_file(relative_path: str, data: bytes | BinaryIO, mime: str = "application/octet-stream") -> str:
    path = get_storage_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_bytes(data.read())
    return relative_path


def read_file(relative_path: str) -> bytes:
    path = get_storage_path(relative_path)
    return path.read_bytes()


def file_exists(relative_path: str) -> bool:
    path = get_storage_path(relative_path)
    return path.is_file()


def get_public_url(relative_path: str) -> str:
    settings = get_settings()
    base = settings.BACKEND_URL.rstrip("/")
    return f"{base}/storage/{relative_path}"
