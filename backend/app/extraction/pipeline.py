from __future__ import annotations

import logging
from typing import Any

from app.extraction.ocr import ocr_image_bytes, ocr_pdf_bytes
from app.extraction.parsers import parse_fields_from_text
from app.extraction.pdf_text import extract_pdf_text

logger = logging.getLogger(__name__)


def _extract_text(mime: str, data: bytes) -> tuple[str, dict[str, Any]]:
    mime_l = (mime or "").lower()
    meta: dict[str, Any] = {"mime": mime_l}
    if "pdf" in mime_l:
        text = extract_pdf_text(data)
        meta["pdf_text_len"] = len(text)
        if len(text.strip()) < 80:
            ocr = ocr_pdf_bytes(data)
            meta["ocr_used"] = True
            meta["ocr_len"] = len(ocr)
            text = (text + "\n" + ocr).strip() if text else ocr
        else:
            meta["ocr_used"] = False
        return text, meta

    # immagini
    ocr = ocr_image_bytes(data)
    meta["ocr_used"] = True
    meta["ocr_len"] = len(ocr)
    return ocr, meta


def compute_confidence(fields_latest: dict[str, Any], fields_older: dict[str, Any] | None, meta: dict[str, Any]) -> int:
    score = 100

    def penalty_if_missing(d: dict[str, Any], key: str, p: int) -> None:
        nonlocal score
        if key not in d or d.get(key) in (None, "", 0):
            score -= p

    # Core sul "latest" (è quello che mostriamo per diagnosi)
    penalty_if_missing(fields_latest, "total_eur", 25)
    if not (fields_latest.get("kwh") or fields_latest.get("mc")):
        score -= 25
    penalty_if_missing(fields_latest, "supplier", 10)
    if not (fields_latest.get("period_start") and fields_latest.get("period_end")):
        score -= 10

    if meta.get("latest", {}).get("ocr_used"):
        score -= 5

    if fields_older:
        # bonus lieve se abbiamo confronto
        score += 3

    score = max(0, min(100, score))
    return int(score)


def extract_fields_from_documents(docs: list[dict[str, Any]]) -> tuple[dict[str, Any], int]:
    """
    docs: [{kind, mime, bytes}]
    return: (fields_json, confidence)
    """
    per_kind: dict[str, dict[str, Any]] = {}
    meta: dict[str, Any] = {}

    for doc in docs:
        kind = doc["kind"]
        mime = doc.get("mime") or "application/octet-stream"
        data: bytes = doc["bytes"]
        text, m = _extract_text(mime, data)
        fields = parse_fields_from_text(text)
        fields["_text_len"] = len(text)
        per_kind[kind] = fields
        meta[kind] = m

    latest = per_kind.get("latest", {})
    older = per_kind.get("older")
    confidence = compute_confidence(latest, older, meta)

    out = {
        "latest": latest,
        "older": older,
        "meta": meta,
    }
    return out, confidence

