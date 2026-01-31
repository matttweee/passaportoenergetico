"""Token/session signing."""
from __future__ import annotations

import hmac
import hashlib
import secrets
from typing import Optional

from app.core.config import get_settings


def sign_token(session_id: str) -> str:
    key = get_settings().SECRET_KEY.encode()
    msg = session_id.encode()
    sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return f"{session_id}.{sig}"


def verify_token(token: str) -> Optional[str]:
    if not token or "." not in token:
        return None
    session_id, sig = token.rsplit(".", 1)
    expected = sign_token(session_id)
    if hmac.compare_digest(expected, token):
        return session_id
    return None


def generate_share_token() -> str:
    return secrets.token_urlsafe(24)
