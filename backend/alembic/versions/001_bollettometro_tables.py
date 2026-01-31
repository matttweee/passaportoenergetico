"""Bollettometro 2030 tables

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, index=True),
        sa.Column("cap", sa.String(16), nullable=True, index=True),
        sa.Column("zone_key", sa.String(64), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
    )
    op.create_table(
        "uploaded_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("doc_type", sa.String(16), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "extracted_bills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("doc_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issue_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_due", sa.Float(), nullable=True),
        sa.Column("kwh", sa.Float(), nullable=True),
        sa.Column("smc", sa.Float(), nullable=True),
        sa.Column("energy_cost", sa.Float(), nullable=True),
        sa.Column("transport_cost", sa.Float(), nullable=True),
        sa.Column("taxes", sa.Float(), nullable=True),
        sa.Column("supplier", sa.String(256), nullable=True),
        sa.Column("tariff_name", sa.String(256), nullable=True),
        sa.Column("raw_json", postgresql.JSONB(), nullable=True),
        sa.Column("confidence_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "trend_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_sessions.id", ondelete="CASCADE"), unique=True, index=True),
        sa.Column("user_trend_json", postgresql.JSONB(), nullable=False),
        sa.Column("zone_trend_json", postgresql.JSONB(), nullable=False),
        sa.Column("position", sa.String(16), nullable=False),
        sa.Column("explanation_short", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "passports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_sessions.id", ondelete="CASCADE"), unique=True, index=True),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("pdf_path", sa.String(1024), nullable=True),
        sa.Column("qr_token", sa.String(128), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "share_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_sessions.id", ondelete="CASCADE"), unique=True, index=True),
        sa.Column("share_image_path", sa.String(1024), nullable=True),
        sa.Column("share_token", sa.String(128), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "map_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("zone_key", sa.String(64), index=True),
        sa.Column("approx_lat", sa.Float(), nullable=False),
        sa.Column("approx_lng", sa.Float(), nullable=False),
        sa.Column("color", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_session_id_hash", sa.String(64), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("map_points")
    op.drop_table("share_artifacts")
    op.drop_table("passports")
    op.drop_table("trend_results")
    op.drop_table("extracted_bills")
    op.drop_table("uploaded_documents")
    op.drop_table("user_sessions")
