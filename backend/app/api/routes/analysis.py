"""Analysis: start job, status."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import UserSession, UploadedDocument
from app.workers.tasks import analyze_session

router = APIRouter(prefix="/analyze", tags=["analysis"])


class StartRequest(BaseModel):
    session_id: str


class StartResponse(BaseModel):
    job_id: str
    status: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    session_status: str | None


@router.post("/start", response_model=StartResponse)
def start_analysis(payload: StartRequest, db: Session = Depends(get_db)):
    try:
        sid = uuid.UUID(payload.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id non valido")
    session = db.get(UserSession, sid)
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    docs = list(db.execute(select(UploadedDocument).where(UploadedDocument.session_id == sid)).scalars().all())
    docs = [d[0] for d in docs]
    if len(docs) < 2:
        raise HTTPException(status_code=400, detail="Carica 2 bollette (recent + old) prima di avviare l'analisi")
    task = analyze_session.delay(str(sid))
    return StartResponse(job_id=task.id, status="running")


@router.get("/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str, session_id: str | None = Query(None), db: Session = Depends(get_db)):
    from celery.result import AsyncResult
    from app.workers.celery_app import app as celery_app
    res = AsyncResult(job_id, app=celery_app)
    status = "pending"
    if res.ready():
        status = "done" if res.successful() else "error"
    elif res.state == "STARTED" or res.state == "PENDING":
        status = "running" if res.state == "STARTED" else "pending"
    session_status = None
    if session_id:
        try:
            sid = uuid.UUID(session_id)
            session = db.get(UserSession, sid)
            if session:
                session_status = session.status
        except Exception:
            pass
    return StatusResponse(job_id=job_id, status=status, session_status=session_status)
