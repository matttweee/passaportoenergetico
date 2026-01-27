from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File as UploadFileDep, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import (
    AnalyzeResponse,
    LeadRequest,
    ReportOut,
    SubmissionCreate,
    SubmissionCreated,
    SubmissionStatus,
    UploadFinalizeRequest,
)
from app.core.config import get_settings
from app.db.models import Finding, Submission
from app.services.reports import get_report_by_token
from app.services.submissions import (
    add_file_record,
    build_presigned_targets,
    create_submission,
    get_submission,
    list_files,
    make_storage_path,
    run_analysis,
    set_analysis_state,
)
from app.storage import get_storage
from app.db.session import get_sessionmaker

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_upload(mime: str, size: int) -> None:
    settings = get_settings()
    allowed = {"application/pdf", "image/jpeg", "image/png"}
    if mime.lower() not in allowed:
        raise HTTPException(status_code=400, detail="Formato non supportato (solo PDF/JPG/PNG)")
    if size > settings.MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File troppo grande (max {settings.MAX_FILE_MB}MB)")


@router.post("/submissions", response_model=SubmissionCreated)
def create_submission_route(payload: SubmissionCreate, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    sub = create_submission(db, email=payload.email, phone=payload.phone, consent=payload.consent, ip=ip)

    storage = get_storage()
    expected = payload.expected_kinds or ["latest", "older"]
    presigned = build_presigned_targets(storage, sub.id, expected)
    return SubmissionCreated(id=sub.id, presigned=presigned)


@router.post("/submissions/{submission_id}/files")
def upload_file_route(
    submission_id: uuid.UUID,
    kind: str,
    file: UploadFile = UploadFileDep(...),
    db: Session = Depends(get_db),
):
    sub = get_submission(db, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission non trovata")

    if kind not in ("latest", "older"):
        raise HTTPException(status_code=400, detail="kind deve essere latest o older")

    data = file.file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="File vuoto (0 bytes)")
    mime = file.content_type or "application/octet-stream"
    _validate_upload(mime, len(data))

    storage = get_storage()
    storage_path = make_storage_path(submission_id, kind, file.filename or f"{kind}")
    storage.save_bytes(data, storage_path, mime=mime)
    rec = add_file_record(
        db,
        submission_id=submission_id,
        original_name=file.filename or "upload",
        mime=mime,
        size=len(data),
        storage_path=storage_path,
        kind=kind,
    )
    return {"ok": True, "file_id": str(rec.id), "storage_path": storage_path}


@router.post("/submissions/{submission_id}/files/finalize")
def finalize_files_route(submission_id: uuid.UUID, payload: UploadFinalizeRequest, db: Session = Depends(get_db)):
    sub = get_submission(db, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission non trovata")
    for item in payload.files:
        _validate_upload(item.mime, item.size)
        add_file_record(
            db,
            submission_id=submission_id,
            original_name=item.original_name,
            mime=item.mime,
            size=item.size,
            storage_path=item.storage_path,
            kind=item.kind,
        )
    return {"ok": True}


@router.put("/storage/local/put")
async def local_presigned_put(path: str, request: Request):
    storage = get_storage()
    raw = await request.body()
    mime = request.headers.get("content-type", "application/octet-stream")
    storage.save_bytes(raw, path, mime=mime)
    return {"ok": True, "path": path}


def _analysis_task(submission_id: uuid.UUID) -> None:
    SessionMaker = get_sessionmaker()
    db = SessionMaker()
    try:
        storage = get_storage()
        run_analysis(db, submission_id, storage)
    finally:
        db.close()


@router.post("/submissions/{submission_id}/analyze", response_model=AnalyzeResponse)
def analyze_route(submission_id: uuid.UUID, bg: BackgroundTasks, db: Session = Depends(get_db)):
    sub = get_submission(db, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission non trovata")

    # basic check: 1-2 file
    files = list_files(db, submission_id)
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Carica almeno 1 bolletta prima dell'analisi")
    if len(files) > 2:
        raise HTTPException(status_code=400, detail="Massimo 2 bollette consentite")

    set_analysis_state(db, sub, "pending", None)
    bg.add_task(_analysis_task, submission_id)
    return AnalyzeResponse(id=submission_id, analysis_state="running")


@router.get("/submissions/{submission_id}/status", response_model=SubmissionStatus)
def status_route(submission_id: uuid.UUID, db: Session = Depends(get_db)):
    sub = get_submission(db, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission non trovata")
    share = sub.share_token if sub.analysis_state == "done" else None
    return SubmissionStatus(
        id=sub.id,
        created_at=sub.created_at,
        status=sub.status,
        analysis_state=sub.analysis_state,  # type: ignore
        analysis_error=sub.analysis_error,
        share_token=share,
    )


@router.get("/report/{share_token}", response_model=ReportOut)
def report_route(share_token: str, db: Session = Depends(get_db)):
    rep = get_report_by_token(db, share_token)
    if not rep:
        raise HTTPException(status_code=404, detail="Report non trovato")
    sub = rep["submission"]
    ex = rep["extracted"]
    findings = rep["findings"]
    # Aggiungi warning come finding se presente
    if rep.get("comparison_warning"):
        from app.db.models import Finding as FindingModel
        warning_finding = {
            "id": str(uuid.uuid4()),
            "severity": "low",
            "title": "Confronto limitato",
            "description": rep["comparison_warning"],
            "estimated_impact_eur": None,
            "rule_id": "COMPARISON_LIMITED",
            "created_at": sub.created_at,
        }
        findings_list = [
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
        ]
        findings_list.insert(0, warning_finding)
    else:
        findings_list = [
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
        ]
    return ReportOut(
        submission_id=sub.id,
        created_at=sub.created_at,
        status=sub.status,
        summary=rep["summary"],
        confidence=int(ex.confidence) if ex else 0,
        extracted=ex.fields if ex else None,
        findings=findings_list,
        comparison_warning=rep.get("comparison_warning"),
    )


@router.post("/report/{share_token}/lead")
def lead_route(share_token: str, payload: LeadRequest, db: Session = Depends(get_db)):
    rep = get_report_by_token(db, share_token)
    if not rep:
        raise HTTPException(status_code=404, detail="Report non trovato")
    sub: Submission = rep["submission"]

    # aggiorna contatti se forniti
    if payload.email:
        sub.email = payload.email
    if payload.phone:
        sub.phone = payload.phone
    sub.status = "contact_requested"
    db.add(sub)
    db.commit()

    # registra come finding (senza cambiare schema DB)
    msg = (payload.message or "").strip()
    db.add(
        Finding(
            submission_id=sub.id,
            severity="low",
            title="Richiesta di correzione",
            description=msg or "L'utente ha richiesto una verifica/correzione.",
            estimated_impact_eur=None,
            rule_id="USER_LEAD",
        )
    )
    db.commit()
    return {"ok": True}

