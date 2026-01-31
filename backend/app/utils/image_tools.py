"""Image handling for bills."""
from __future__ import annotations

import base64
import io
import logging

logger = logging.getLogger(__name__)


def image_bytes_to_base64(data: bytes, mime: str = "image/jpeg") -> str:
    """Encode image bytes for OpenAI vision."""
    return base64.standard_b64encode(data).decode("ascii")


def resize_if_large(data: bytes, max_size: int = 1024) -> bytes:
    """Resize image if larger than max_size on longest side."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data)).convert("RGB")
        w, h = img.size
        if max(w, h) <= max_size:
            return data
        ratio = max_size / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception as e:
        logger.warning("resize failed: %s", e)
        return data
