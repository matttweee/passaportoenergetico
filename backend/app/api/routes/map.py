"""Map: commit point, get zone points (gated)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import UserSession, TrendResult
from app.services.map_service import add_map_point, get_zone_points, coverage_opacity

router = APIRouter(prefix="/map", tags=["map"])


class CommitRequest(BaseModel):
    session_id: str


class CommitResponse(BaseModel):
    ok: bool


class MapPointsResponse(BaseModel):
    zone_key: str
    points: list[dict]
    coverage_opacity: float


@router.post("/commit", response_model=CommitResponse)
def commit_point(payload: CommitRequest, db: Session = Depends(get_db)):
    try:
        sid = uuid.UUID(payload.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id non valido")
    session = db.get(UserSession, sid)
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    if session.status != "verified":
        raise HTTPException(status_code=403, detail="Verifica completata richiesta")
    tr = db.query(TrendResult).filter(TrendResult.session_id == sid).first()
    if not tr:
        raise HTTPException(status_code=403, detail="Risultato non trovato")
    zone_key = session.zone_key or "unknown"
    cap = session.cap or "00100"
    add_map_point(db, str(sid), zone_key, tr.position, cap)
    return CommitResponse(ok=True)


@router.get("/{zone_key}", response_model=MapPointsResponse)
def get_map(zone_key: str, db: Session = Depends(get_db)):
    points = get_zone_points(db, zone_key)
    opacity = coverage_opacity(len(points))
    return MapPointsResponse(zone_key=zone_key, points=points, coverage_opacity=opacity)
