from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    email: str | None = None
    phone: str | None = None
    consent: bool = False
    expected_kinds: list[Literal["latest", "older"]] | None = None


class PresignedTarget(BaseModel):
    kind: Literal["latest", "older"]
    upload_url: str
    storage_path: str


class SubmissionCreated(BaseModel):
    id: UUID
    presigned: list[PresignedTarget] = []


class UploadFinalizeItem(BaseModel):
    kind: Literal["latest", "older"]
    original_name: str
    mime: str
    size: int
    storage_path: str


class UploadFinalizeRequest(BaseModel):
    files: list[UploadFinalizeItem]


class SubmissionStatus(BaseModel):
    id: UUID
    created_at: datetime
    status: str
    analysis_state: Literal["pending", "running", "done", "error"]
    analysis_error: str | None = None
    share_token: str | None = None


class AnalyzeResponse(BaseModel):
    id: UUID
    analysis_state: str


class FindingOut(BaseModel):
    id: UUID
    severity: Literal["low", "med", "high"]
    title: str
    description: str
    estimated_impact_eur: float | None
    rule_id: str
    created_at: datetime


class ReportOut(BaseModel):
    submission_id: UUID
    created_at: datetime
    status: str
    summary: Literal["OK", "ATTENZIONE", "CRITICO"]
    confidence: int
    extracted: dict[str, Any] | None
    findings: list[FindingOut]
    comparison_warning: str | None = None


class AdminLoginRequest(BaseModel):
    password: str = Field(min_length=1)


class AdminMe(BaseModel):
    ok: bool = True


class AdminSubmissionListItem(BaseModel):
    id: UUID
    created_at: datetime
    status: str
    email: str | None
    phone: str | None
    consent: bool
    analysis_state: str


class AdminSubmissionDetail(BaseModel):
    id: UUID
    created_at: datetime
    status: str
    email: str | None
    phone: str | None
    consent: bool
    ip: str | None
    share_token: str
    analysis_state: str
    analysis_error: str | None
    files: list[dict[str, Any]]
    extracted: dict[str, Any] | None
    confidence: int | None
    findings: list[FindingOut]


class AdminStatusUpdate(BaseModel):
    status: str


class LeadRequest(BaseModel):
    message: str | None = None
    email: str | None = None
    phone: str | None = None

