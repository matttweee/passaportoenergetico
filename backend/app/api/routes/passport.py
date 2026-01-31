"""Passport: generate PDF."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import sign_token
from app.db.models import UserSession, TrendResult, Passport
from app.services.passport_generator import generate_passport_pdf
from app.core.config import get_settings

router = APIRouter(prefix="/passport", tags=["passport"])


class GenerateRequest(BaseModel):
    session_id: str


class GenerateResponse(BaseModel):
    pdf_url: str
    qr_token: str


@router.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest, db: Session = Depends(get_db)):
    try:
        sid = uuid.UUID(payload.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id non valido")
    session = db.get(UserSession, sid)
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    if session.status != "verified":
        raise HTTPException(status_code=403, detail="Completa l'analisi prima")
    tr = db.query(TrendResult).filter(TrendResult.session_id == sid).first()
    if not tr:
        raise HTTPException(status_code=404, detail="Risultato non trovato")
    passport = db.query(Passport).filter(Passport.session_id == sid).first()
    base = get_settings().BACKEND_URL.rstrip("/")
    if passport and passport.pdf_path:
        return GenerateResponse(
            pdf_url=f"{base}/api/storage/{passport.pdf_path}",
            qr_token=passport.qr_token or sign_token(str(sid)),
        )
    qr_token = sign_token(str(sid))
    zone_label = session.zone_key or session.cap or "Zona"
    pdf_path = generate_passport_pdf(str(sid), zone_label, tr.position, qr_token)
    if not passport:
        passport = Passport(session_id=sid, status="ready", pdf_path=pdf_path, qr_token=qr_token)
        db.add(passport)
    else:
        passport.pdf_path = pdf_path
        passport.qr_token = qr_token
        passport.status = "ready"
    db.commit()
    return GenerateResponse(pdf_url=f"{base}/api/storage/{pdf_path}", qr_token=qr_token)
