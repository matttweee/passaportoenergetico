from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Iterable

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Extracted, File, Finding, Submission
from app.extraction.pipeline import extract_fields_from_documents
from app.rules.engine import run_rules
from app.rules.ruleset import RuleFinding
from app.storage.base import Storage

logger = logging.getLogger(__name__)


def create_submission(
    db: Session,
    *,
    email: str | None,
    phone: str | None,
    consent: bool,
    ip: str | None,
) -> Submission:
    sub = Submission(email=email, phone=phone, consent=consent, ip=ip)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def get_submission(db: Session, submission_id: uuid.UUID) -> Submission | None:
    return db.get(Submission, submission_id)


def list_files(db: Session, submission_id: uuid.UUID) -> list[File]:
    return list(db.scalars(select(File).where(File.submission_id == submission_id).order_by(File.created_at)))


def add_file_record(
    db: Session,
    *,
    submission_id: uuid.UUID,
    original_name: str,
    mime: str,
    size: int,
    storage_path: str,
    kind: str,
) -> File:
    f = File(
        submission_id=submission_id,
        original_name=original_name,
        mime=mime,
        size=size,
        storage_path=storage_path,
        kind=kind,
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def make_storage_path(submission_id: uuid.UUID, kind: str, original_name: str) -> str:
    safe_name = original_name.replace("\\", "_").replace("/", "_")
    return f"submissions/{submission_id}/{kind}/{uuid.uuid4()}_{safe_name}"


def build_presigned_targets(storage: Storage, submission_id: uuid.UUID, expected_kinds: list[str]) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    for kind in expected_kinds:
        storage_path = make_storage_path(submission_id, kind, f"{kind}.bin")
        upload_url = storage.get_presigned_put_url(storage_path, mime="application/octet-stream") or ""
        targets.append({"kind": kind, "storage_path": storage_path, "upload_url": upload_url})
    return targets


def set_analysis_state(db: Session, submission: Submission, state: str, error: str | None = None) -> None:
    submission.analysis_state = state
    submission.analysis_error = error
    db.add(submission)
    db.commit()


def run_analysis(db: Session, submission_id: uuid.UUID, storage: Storage) -> None:
    """Esegue estrazione + regole e persiste risultati. Mai lanciare eccezioni verso l'esterno."""
    sub = get_submission(db, submission_id)
    if not sub:
        return

    try:
        set_analysis_state(db, sub, "running", None)

        files = list_files(db, submission_id)
        if len(files) == 0:
            set_analysis_state(db, sub, "error", "Nessun file caricato")
            return

        docs: list[dict[str, Any]] = []
        for f in files:
            try:
                data = storage.read_bytes(f.storage_path)
                if len(data) == 0:
                    raise ValueError(f"File {f.original_name} è vuoto (0 bytes)")
                docs.append({"kind": f.kind, "mime": f.mime, "bytes": data})
            except Exception as e:
                logger.warning(f"Failed to read file {f.id}: {e}")
                set_analysis_state(db, sub, "error", f"Errore lettura file {f.original_name}: {str(e)[:200]}")
                return

        extracted_fields, confidence = extract_fields_from_documents(docs)

        # reset risultati precedenti
        db.execute(delete(Finding).where(Finding.submission_id == submission_id))
        db.execute(delete(Extracted).where(Extracted.submission_id == submission_id))
        db.commit()

        ex = Extracted(submission_id=submission_id, fields=extracted_fields, confidence=int(confidence))
        db.add(ex)

        rule_findings: list[RuleFinding] = run_rules(extracted_fields)
        for rf in rule_findings:
            db.add(
                Finding(
                    submission_id=submission_id,
                    severity=rf.severity,
                    title=rf.title,
                    description=rf.description,
                    estimated_impact_eur=rf.estimated_impact_eur,
                    rule_id=rf.rule_id,
                )
            )

        db.commit()
        set_analysis_state(db, sub, "done", None)
    except Exception as e:
        logger.exception("analysis_failed", extra={"submission_id": str(submission_id)})
        set_analysis_state(db, sub, "error", str(e))

