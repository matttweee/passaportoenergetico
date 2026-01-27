from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, GUID


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_share_token() -> str:
    return secrets.token_urlsafe(24)  # ~32 chars


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    share_token: Mapped[str] = mapped_column(String(64), unique=True, default=generate_share_token, nullable=False)
    analysis_state: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    analysis_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    files: Mapped[list["File"]] = relationship(back_populates="submission", cascade="all, delete-orphan")
    extracted: Mapped["Extracted | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
    findings: Mapped[list["Finding"]] = relationship(back_populates="submission", cascade="all, delete-orphan")


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("submissions.id", ondelete="CASCADE"), index=True)
    original_name: Mapped[str] = mapped_column(String(512), nullable=False)
    mime: Mapped[str] = mapped_column(String(128), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # latest|older
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)

    submission: Mapped["Submission"] = relationship(back_populates="files")


class Extracted(Base):
    __tablename__ = "extracted"

    submission_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    fields: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)

    submission: Mapped["Submission"] = relationship(back_populates="extracted")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("submissions.id", ondelete="CASCADE"), index=True)
    severity: Mapped[str] = mapped_column(String(8), nullable=False)  # low|med|high
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_impact_eur: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    rule_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)

    submission: Mapped["Submission"] = relationship(back_populates="findings")

