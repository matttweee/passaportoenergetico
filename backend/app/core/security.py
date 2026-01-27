from __future__ import annotations

import base64
import hmac
import hashlib
import json
import time
from typing import Any


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + padding).encode("utf-8"))


def sign_admin_session(secret_key: str, issued_at: int | None = None) -> str:
    ts = issued_at or int(time.time())
    payload = {"iat": ts}
    payload_b = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    sig = hmac.new(secret_key.encode("utf-8"), payload_b, hashlib.sha256).digest()
    return f"{_b64url(payload_b)}.{_b64url(sig)}"


def verify_admin_session(secret_key: str, token: str, max_age_seconds: int = 60 * 60 * 12) -> bool:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return False
        payload_b = _b64url_decode(parts[0])
        sig_b = _b64url_decode(parts[1])
        expected = hmac.new(secret_key.encode("utf-8"), payload_b, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, sig_b):
            return False
        payload: dict[str, Any] = json.loads(payload_b.decode("utf-8"))
        iat = int(payload.get("iat", 0))
        if iat <= 0:
            return False
        if int(time.time()) - iat > max_age_seconds:
            return False
        return True
    except Exception:
        return False

