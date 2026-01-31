"""Result: get by session_id + token."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import verify_token
from app.db.models import UserSession, TrendResult, Passport, ShareArtifact
from app.core.config import get_settings

router = APIRouter(prefix="/result", tags=["result"])


class ResultResponse(BaseModel):
    session_id: str
    position: str
    explanation_short: str
    user_trend_json: dict
    zone_trend_json: dict
    passport_pdf_url: str | None
    share_image_url: str | None
    share_token: str | None


@router.get("/{session_id}", response_model=ResultResponse)
def get_result(
    session_id: str,
    t: str | None = Query(None, alias="t"),
    db: Session = Depends(get_db),
):
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id non valido")
    if t and verify_token(t) != session_id:
        raise HTTPException(status_code=403, detail="Token non valido")
    session = db.get(UserSession, sid)
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    if session.status != "verified":
        raise HTTPException(status_code=403, detail="Analisi non ancora completata o non valida")
    tr = db.query(TrendResult).filter(TrendResult.session_id == sid).first()
    if not tr:
        raise HTTPException(status_code=404, detail="Risultato non trovato")
    passport = db.query(Passport).filter(Passport.session_id == sid).first()
    share_art = db.query(ShareArtifact).filter(ShareArtifact.session_id == sid).first()
    base = get_settings().BACKEND_URL.rstrip("/")
    passport_url = f"{base}/api/storage/{passport.pdf_path}" if passport and passport.pdf_path else None
    share_url = f"{base}/api/storage/{share_art.share_image_path}" if share_art and share_art.share_image_path else None
    return ResultResponse(
        session_id=session_id,
        position=tr.position,
        explanation_short=tr.explanation_short,
        user_trend_json=tr.user_trend_json or {},
        zone_trend_json=tr.zone_trend_json or {},
        passport_pdf_url=passport_url,
        share_image_url=share_url,
        share_token=share_art.share_token if share_art else None,
    )
