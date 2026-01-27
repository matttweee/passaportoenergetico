from __future__ import annotations

import io
import logging

import pdfplumber

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            parts: list[str] = []
            for page in pdf.pages:
                t = page.extract_text() or ""
                if t.strip():
                    parts.append(t)
            return "\n".join(parts).strip()
    except Exception:
        logger.exception("pdf_text_extract_failed")
        return ""

