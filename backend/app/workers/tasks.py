"""Celery tasks: analyze_session, TTL cleanup."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings
from app.db.base import Base
from app.db.models import (
    UserSession,
    UploadedDocument,
    ExtractedBill,
    TrendResult,
    Passport,
)
from app.services.storage import read_file, file_exists
from app.services.openai_extract import extract_from_text, extract_from_image_base64
from app.services.extract_schema import ExtractionOutput, validate_extraction_payload
from app.services.trend_calc import compute_user_trend, compute_position
from app.services.zone_aggregates import get_zone_trend_json, cap_to_zone_key
from app.utils.pdf_tools import extract_text_from_pdf, extract_first_page_image
from app.utils.image_tools import image_bytes_to_base64, resize_if_large

logger = logging.getLogger(__name__)

from app.workers.celery_app import app


def _get_db() -> Session:
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    sm = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return sm()


def _extract_one(doc: UploadedDocument) -> dict | None:
    """Extract one document to raw dict (for ExtractedBill.raw_json)."""
    data = read_file(doc.file_path)
    mime = (doc.mime_type or "").lower()
    text = ""
    if "pdf" in mime:
        text = extract_text_from_pdf(data)
        if not text.strip():
            img_bytes = extract_first_page_image(data)
            if img_bytes:
                b64 = image_bytes_to_base64(resize_if_large(img_bytes))
                out, err = extract_from_image_base64(b64)
                return out
        out, err = extract_from_text(text)
        return out if not err else None
    if "image" in mime:
        b64 = image_bytes_to_base64(resize_if_large(data))
        out, err = extract_from_image_base64(b64)
        return out if not err else None
    return None


def _bill_dict_to_orm(raw: dict, session_id: uuid.UUID, doc_id: uuid.UUID) -> dict:
    """Convert extraction dict to ExtractedBill fields."""
    from datetime import date as date_type
    out, _ = validate_extraction_payload(raw)
    if not out:
        return {}
    def to_dt(d: date_type | None):
        if d is None:
            return None
        return datetime.combine(d, datetime.min.time()).replace(tzinfo=timezone.utc)
    d = {
        "session_id": session_id,
        "doc_id": doc_id,
        "period_start": to_dt(out.period_start),
        "period_end": to_dt(out.period_end),
        "issue_date": to_dt(out.issue_date),
        "total_due": out.total_due,
        "kwh": out.kwh,
        "smc": out.smc,
        "energy_cost": out.energy_cost,
        "transport_cost": out.transport_cost,
        "taxes": out.taxes,
        "supplier": out.supplier,
        "tariff_name": out.tariff_name,
        "raw_json": raw,
        "confidence_json": out.confidence.model_dump() if out.confidence else None,
    }
    return d


@app.task(bind=True, name="analyze_session")
def analyze_session(self, session_id: str):
    """Load docs, extract with OpenAI, compute trend, store result, mark VERIFIED."""
    sid = uuid.UUID(session_id)
    db = _get_db()
    try:
        session = db.get(UserSession, sid)
        if not session:
            logger.error("Session not found: %s", session_id)
            return
        docs = list(db.execute(select(UploadedDocument).where(UploadedDocument.session_id == sid).order_by(UploadedDocument.doc_type)).scalars().all())
        docs = [d[0] for d in docs]
        if len(docs) < 2:
            session.status = "error"
            db.commit()
            return
        recent_doc = next((d for d in docs if d.doc_type == "recent"), None)
        old_doc = next((d for d in docs if d.doc_type == "old"), None)
        if not recent_doc or not old_doc:
            session.status = "error"
            db.commit()
            return

        raw_recent = _extract_one(recent_doc)
        raw_old = _extract_one(old_doc)
        if not raw_recent or not raw_old:
            session.status = "error"
            db.commit()
            return

        for doc, raw in [(recent_doc, raw_recent), (old_doc, raw_old)]:
            row = _bill_dict_to_orm(raw, sid, doc.id)
            if row:
                eb = ExtractedBill(**row)
                db.add(eb)
        db.commit()

        user_trend = compute_user_trend(raw_recent, raw_old)
        zone_key = session.zone_key or cap_to_zone_key(session.cap or "")
        zone_trend = get_zone_trend_json(db, zone_key)
        position, explanation = compute_position(user_trend, zone_trend)

        tr = TrendResult(
            session_id=sid,
            user_trend_json=user_trend,
            zone_trend_json=zone_trend,
            position=position,
            explanation_short=explanation,
        )
        db.add(tr)
        session.status = "verified"
        db.commit()
        logger.info("Session %s verified, position=%s", session_id, position)
    except Exception as e:
        logger.exception("analyze_session failed: %s", e)
        try:
            session = db.get(UserSession, sid)
            if session:
                session.status = "error"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@app.task(name="ttl_cleanup")
def ttl_cleanup():
    """Delete raw uploads older than UPLOAD_TTL_HOURS. Keep extracted data."""
    from pathlib import Path
    from app.services.storage import get_storage_path
    settings = get_settings()
    try:
        base = Path(settings.LOCAL_STORAGE_PATH)
        if not base.exists():
            return
        cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.UPLOAD_TTL_HOURS)
        for f in base.rglob("*"):
            if f.is_file() and f.stat().st_mtime < cutoff.timestamp():
                try:
                    f.unlink()
                except Exception as e:
                    logger.warning("TTL delete failed %s: %s", f, e)
    except Exception as e:
        logger.exception("TTL cleanup failed: %s", e)
