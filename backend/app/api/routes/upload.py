"""Upload: file + doc_type (recent|old)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.db.models import UserSession, UploadedDocument
from app.services.storage import save_file
from app.utils.validation import validate_doc_type, validate_mime, validate_file_size

router = APIRouter(prefix="/upload", tags=["upload"])


class UploadResponse(BaseModel):
    doc_id: str
    file_path: str


@router.post("", response_model=UploadResponse)
async def upload(
    session_id: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not validate_doc_type(doc_type):
        raise HTTPException(status_code=400, detail="doc_type deve essere recent o old")
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id non valido")
    session = db.get(UserSession, sid)
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="File vuoto")
    mime = file.content_type or "application/octet-stream"
    if not validate_mime(mime):
        raise HTTPException(status_code=400, detail="Formato non supportato (PDF/JPG/PNG)")
    max_mb = get_settings().MAX_FILE_MB
    if not validate_file_size(len(data), max_mb):
        raise HTTPException(status_code=400, detail=f"File troppo grande (max {max_mb}MB)")
    rel_path = f"uploads/{sid}/{doc_type}_{uuid.uuid4().hex[:8]}.{file.filename or 'bin'}"
    save_file(rel_path, data, mime=mime)
    doc = UploadedDocument(
        session_id=sid,
        doc_type=doc_type,
        file_path=rel_path,
        mime_type=mime,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return UploadResponse(doc_id=str(doc.id), file_path=rel_path)
