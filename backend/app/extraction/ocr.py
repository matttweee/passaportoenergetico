from __future__ import annotations

import io
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def _ocr_image(img: Image.Image) -> str:
    # Piccolo pre-processing per bollette scansionate
    gray = ImageOps.grayscale(img)
    return (pytesseract.image_to_string(gray, lang="ita") or "").strip()


def ocr_image_bytes(image_bytes: bytes) -> str:
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            return _ocr_image(img)
    except Exception:
        logger.exception("ocr_image_failed")
        return ""


def ocr_pdf_bytes(pdf_bytes: bytes, dpi: int = 200, max_pages: int | None = None) -> str:
    """OCR PDF via poppler `pdftoppm` -> PNG -> tesseract.

    Richiede `poppler-utils` nel container.
    """
    from app.core.config import get_settings
    settings = get_settings()
    if max_pages is None:
        max_pages = settings.OCR_MAX_PAGES
    try:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            pdf_path = td_path / "input.pdf"
            pdf_path.write_bytes(pdf_bytes)
            out_prefix = td_path / "page"

            # -f/-l per limitare numero pagine (performance)
            cmd = [
                "pdftoppm",
                "-png",
                "-r",
                str(dpi),
                "-f",
                "1",
                "-l",
                str(max_pages),
                str(pdf_path),
                str(out_prefix),
            ]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            texts: list[str] = []
            for img_path in sorted(td_path.glob("page-*.png")):
                try:
                    with Image.open(img_path) as img:
                        t = _ocr_image(img)
                        if t:
                            texts.append(t)
                except Exception:
                    logger.exception("ocr_pdf_page_failed")
            return "\n".join(texts).strip()
    except Exception:
        logger.exception("ocr_pdf_failed")
        return ""

