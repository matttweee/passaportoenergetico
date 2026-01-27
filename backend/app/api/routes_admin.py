from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.api.schemas import (
    AdminLoginRequest,
    AdminMe,
    AdminStatusUpdate,
    AdminSubmissionDetail,
    AdminSubmissionListItem,
)
from app.core.config import get_settings
from app.core.security import sign_admin_session
from app.db.models import Extracted, File, Finding, Submission
from app.storage import get_storage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login")
def admin_login(payload: AdminLoginRequest, response: Response):
    settings = get_settings()
    if payload.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password errata")
    key = f"{settings.SECRET_KEY}|{settings.ADMIN_PASSWORD}"
    token = sign_admin_session(key)
    is_secure = settings.is_production()
    response.set_cookie(
        key="pe_admin",
        value=token,
        httponly=True,
        samesite="lax",
        secure=is_secure,
        max_age=60 * 60 * 12,
    )
    return {"ok": True}


@router.get("/me", response_model=AdminMe, dependencies=[Depends(require_admin)])
def admin_me():
    return AdminMe(ok=True)


@router.get("/submissions", response_model=list[AdminSubmissionListItem], dependencies=[Depends(require_admin)])
def list_submissions(db: Session = Depends(get_db)):
    subs = list(db.scalars(select(Submission).order_by(Submission.created_at.desc()).limit(50)))
    return [
        AdminSubmissionListItem(
            id=s.id,
            created_at=s.created_at,
            status=s.status,
            email=s.email,
            phone=s.phone,
            consent=s.consent,
            analysis_state=s.analysis_state,
        )
        for s in subs
    ]


@router.get("/submissions/{submission_id}", response_model=AdminSubmissionDetail, dependencies=[Depends(require_admin)])
def get_submission_detail(submission_id: uuid.UUID, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission non trovata")
    files = list(db.scalars(select(File).where(File.submission_id == submission_id).order_by(File.created_at)))
    ex = db.get(Extracted, submission_id)
    findings = list(db.scalars(select(Finding).where(Finding.submission_id == submission_id).order_by(Finding.created_at)))
    return AdminSubmissionDetail(
        id=sub.id,
        created_at=sub.created_at,
        status=sub.status,
        email=sub.email,
        phone=sub.phone,
        consent=sub.consent,
        ip=sub.ip,
        share_token=sub.share_token,
        analysis_state=sub.analysis_state,
        analysis_error=sub.analysis_error,
        files=[
            {
                "id": f.id,
                "original_name": f.original_name,
                "mime": f.mime,
                "size": f.size,
                "storage_path": f.storage_path,
                "kind": f.kind,
                "created_at": f.created_at,
            }
            for f in files
        ],
        extracted=ex.fields if ex else None,
        confidence=int(ex.confidence) if ex else None,
        findings=[
            {
                "id": f.id,
                "severity": f.severity,
                "title": f.title,
                "description": f.description,
                "estimated_impact_eur": float(f.estimated_impact_eur) if f.estimated_impact_eur is not None else None,
                "rule_id": f.rule_id,
                "created_at": f.created_at,
            }
            for f in findings
        ],
    )


@router.post("/submissions/{submission_id}/status", dependencies=[Depends(require_admin)])
def update_status(submission_id: uuid.UUID, payload: AdminStatusUpdate, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission non trovata")
    sub.status = payload.status
    db.add(sub)
    db.commit()
    return {"ok": True}


@router.get("/files/{file_id}/download", dependencies=[Depends(require_admin)])
def download_file(file_id: uuid.UUID, db: Session = Depends(get_db)):
    f = db.get(File, file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File non trovato")
    storage = get_storage()
    data = storage.read_bytes(f.storage_path)
    # Escape filename per header (RFC 5987)
    import urllib.parse
    safe_name = urllib.parse.quote(f.original_name.encode("utf-8"))
    headers = {
        "Content-Disposition": f'attachment; filename="{f.original_name}"; filename*=UTF-8\'\'{safe_name}',
        "Content-Type": f.mime,
        "Content-Length": str(len(data)),
    }
    return StreamingResponse(iter([data]), media_type=f.mime, headers=headers)

