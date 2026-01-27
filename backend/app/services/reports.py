from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Extracted, Finding, Submission


def compute_summary(findings: list[Finding]) -> str:
    if any(f.severity == "high" for f in findings):
        return "CRITICO"
    if any(f.severity == "med" for f in findings):
        return "ATTENZIONE"
    return "OK"


def get_report_by_token(db: Session, share_token: str) -> dict[str, Any] | None:
    sub = db.scalar(select(Submission).where(Submission.share_token == share_token))
    if not sub:
        return None

    ex = db.get(Extracted, sub.id)
    findings = list(db.scalars(select(Finding).where(Finding.submission_id == sub.id).order_by(Finding.created_at)))
    summary = compute_summary(findings)

    # Aggiungi warning se solo 1 file
    from app.services.submissions import list_files
    files = list_files(db, sub.id)
    comparison_warning = None
    if len(files) == 1:
        comparison_warning = "Confronto limitato: è stata caricata solo 1 bolletta. Per un'analisi completa, carica anche una bolletta precedente."

    return {
        "submission": sub,
        "extracted": ex,
        "findings": findings,
        "summary": summary,
        "comparison_warning": comparison_warning,
    }

