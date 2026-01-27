"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-01-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("consent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("share_token", sa.String(length=64), nullable=False),
        sa.Column("analysis_state", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("analysis_error", sa.Text(), nullable=True),
    )
    op.create_index("ix_submissions_created_at", "submissions", ["created_at"])
    op.create_index("ix_submissions_status", "submissions", ["status"])
    op.create_unique_constraint("uq_submissions_share_token", "submissions", ["share_token"])

    op.create_table(
        "files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_name", sa.String(length=512), nullable=False),
        sa.Column("mime", sa.String(length=128), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_files_submission_id", "files", ["submission_id"])
    op.create_index("ix_files_created_at", "files", ["created_at"])

    op.create_table(
        "extracted",
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_extracted_created_at", "extracted", ["created_at"])

    op.create_table(
        "findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(length=8), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("estimated_impact_eur", sa.Numeric(12, 2), nullable=True),
        sa.Column("rule_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_findings_submission_id", "findings", ["submission_id"])
    op.create_index("ix_findings_created_at", "findings", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_findings_created_at", table_name="findings")
    op.drop_index("ix_findings_submission_id", table_name="findings")
    op.drop_table("findings")

    op.drop_index("ix_extracted_created_at", table_name="extracted")
    op.drop_table("extracted")

    op.drop_index("ix_files_created_at", table_name="files")
    op.drop_index("ix_files_submission_id", table_name="files")
    op.drop_table("files")

    op.drop_constraint("uq_submissions_share_token", "submissions", type_="unique")
    op.drop_index("ix_submissions_status", table_name="submissions")
    op.drop_index("ix_submissions_created_at", table_name="submissions")
    op.drop_table("submissions")

