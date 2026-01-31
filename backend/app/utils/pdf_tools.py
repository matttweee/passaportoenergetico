"""PDF text extraction for bill content."""
from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(data: bytes) -> str:
    """Extract raw text from PDF bytes. Returns empty string on failure."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            parts = []
            for i, page in enumerate(pdf.pages[:5]):
                text = page.extract_text()
                if text:
                    parts.append(text)
            return "\n".join(parts) if parts else ""
    except Exception as e:
        logger.warning("pdfplumber failed: %s", e)
        return ""


def extract_first_page_image(data: bytes) -> bytes | None:
    """First page as image bytes (PNG) for vision API. None on failure."""
    try:
        import pdf2image
        images = pdf2image.convert_from_bytes(data, first_page=1, last_page=1, dpi=150)
        if not images:
            return None
        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        logger.warning("pdf2image failed: %s", e)
        return None
