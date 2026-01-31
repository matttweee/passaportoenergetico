"""Share: generate card + token."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import generate_share_token
from app.db.models import UserSession, ShareArtifact
from app.services.share_card_generator import generate_share_card
from app.core.config import get_settings

router = APIRouter(prefix="/share", tags=["share"])


class GenerateRequest(BaseModel):
    session_id: str


class GenerateResponse(BaseModel):
    share_image_url: str
    share_token: str


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
    art = db.query(ShareArtifact).filter(ShareArtifact.session_id == sid).first()
    base = get_settings().BACKEND_URL.rstrip("/")
    if art and art.share_image_path:
        return GenerateResponse(
            share_image_url=f"{base}/api/storage/{art.share_image_path}",
            share_token=art.share_token or generate_share_token(),
        )
    share_token = generate_share_token()
    img_path = generate_share_card(str(sid), share_token)
    if not art:
        art = ShareArtifact(session_id=sid, share_image_path=img_path, share_token=share_token)
        db.add(art)
    else:
        art.share_image_path = img_path
        art.share_token = share_token
    db.commit()
    return GenerateResponse(share_image_url=f"{base}/api/storage/{img_path}", share_token=share_token)
