"""Bollettometro 2030 - SQLAlchemy models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, GUID


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    status: Mapped[str] = mapped_column(String(32), default="started", index=True)
    cap: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    zone_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    documents: Mapped[list["UploadedDocument"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    extracted_bills: Mapped[list["ExtractedBill"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    trend_result: Mapped["TrendResult | None"] = relationship(back_populates="session", uselist=False, cascade="all, delete-orphan")
    passport: Mapped["Passport | None"] = relationship(back_populates="session", uselist=False, cascade="all, delete-orphan")
    share_artifact: Mapped["ShareArtifact | None"] = relationship(back_populates="session", uselist=False, cascade="all, delete-orphan")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("user_sessions.id", ondelete="CASCADE"), index=True)
    doc_type: Mapped[str] = mapped_column(String(16), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    session: Mapped["UserSession"] = relationship(back_populates="documents")
    extracted_bill: Mapped["ExtractedBill | None"] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")


class ExtractedBill(Base):
    __tablename__ = "extracted_bills"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("user_sessions.id", ondelete="CASCADE"), index=True)
    doc_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    issue_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_due: Mapped[float | None] = mapped_column(Float, nullable=True)
    kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    smc: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    transport_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    taxes: Mapped[float | None] = mapped_column(Float, nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tariff_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    confidence_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    session: Mapped["UserSession"] = relationship(back_populates="extracted_bills")
    document: Mapped["UploadedDocument"] = relationship(back_populates="extracted_bill")


class TrendResult(Base):
    __tablename__ = "trend_results"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("user_sessions.id", ondelete="CASCADE"), unique=True, index=True)
    user_trend_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    zone_trend_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    position: Mapped[str] = mapped_column(String(16), nullable=False)
    explanation_short: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    session: Mapped["UserSession"] = relationship(back_populates="trend_result")


class Passport(Base):
    __tablename__ = "passports"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("user_sessions.id", ondelete="CASCADE"), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    pdf_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    qr_token: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    session: Mapped["UserSession"] = relationship(back_populates="passport")


class ShareArtifact(Base):
    __tablename__ = "share_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("user_sessions.id", ondelete="CASCADE"), unique=True, index=True)
    share_image_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    share_token: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    session: Mapped["UserSession"] = relationship(back_populates="share_artifact")


class MapPoint(Base):
    __tablename__ = "map_points"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    zone_key: Mapped[str] = mapped_column(String(64), index=True)
    approx_lat: Mapped[float] = mapped_column(Float, nullable=False)
    approx_lng: Mapped[float] = mapped_column(Float, nullable=False)
    color: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    source_session_id_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
