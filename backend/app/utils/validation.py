"""Input validation helpers."""
from __future__ import annotations

import re
from typing import Any


ALLOWED_MIME = {"application/pdf", "image/jpeg", "image/png", "image/jpg"}
DOC_TYPES = {"recent", "old"}


def validate_cap(cap: str) -> str | None:
    """Italian CAP: 5 digits."""
    if not cap or not isinstance(cap, str):
        return None
    cap = cap.strip().replace(" ", "")
    if re.match(r"^\d{5}$", cap):
        return cap
    return None


def validate_doc_type(doc_type: str) -> bool:
    return doc_type in DOC_TYPES


def validate_mime(mime: str) -> bool:
    return (mime or "").lower().split(";")[0].strip() in ALLOWED_MIME


def validate_file_size(size: int, max_mb: int = 15) -> bool:
    return 0 < size <= max_mb * 1024 * 1024
