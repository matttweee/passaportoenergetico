"""Session: start, set-zone."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import UserSession
from app.services.zone_aggregates import cap_to_zone_key
from app.utils.validation import validate_cap

router = APIRouter(prefix="/session", tags=["session"])


class StartResponse(BaseModel):
    session_id: str
    next_step: str


class SetZoneRequest(BaseModel):
    session_id: str
    cap: str


class SetZoneResponse(BaseModel):
    zone_key: str
    next_step: str


@router.post("/start", response_model=StartResponse)
def start(db: Session = Depends(get_db)):
    session = UserSession(status="started")
    db.add(session)
    db.commit()
    db.refresh(session)
    return StartResponse(session_id=str(session.id), next_step="set_zone")


@router.post("/set-zone", response_model=SetZoneResponse)
def set_zone(payload: SetZoneRequest, db: Session = Depends(get_db)):
    cap = validate_cap(payload.cap)
    if not cap:
        raise HTTPException(status_code=400, detail="CAP non valido (5 cifre)")
    try:
        sid = uuid.UUID(payload.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id non valido")
    session = db.get(UserSession, sid)
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    zone_key = cap_to_zone_key(cap)
    session.cap = cap
    session.zone_key = zone_key
    session.status = "zone_set"
    db.add(session)
    db.commit()
    return SetZoneResponse(zone_key=zone_key, next_step="upload")

