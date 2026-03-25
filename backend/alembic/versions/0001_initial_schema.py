"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "qa", "site", name="userrole"),
            nullable=False,
            server_default="qa",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    # iso_drawings
    op.create_table(
        "iso_drawings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("project_name", sa.String(), nullable=False, server_default=""),
        sa.Column("line_number", sa.String(), nullable=True),
        sa.Column("pipe_size", sa.String(), nullable=True),
        sa.Column("spec", sa.String(), nullable=True),
        sa.Column("weld_count", sa.Integer(), nullable=True),
        sa.Column("raw_ocr_text", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "processed", "error", name="isostatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
    )

    # line_list_entries
    op.create_table(
        "line_list_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("iso_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iso_drawings.id"), nullable=True),
        sa.Column("batch_id", sa.String(), nullable=False),
        sa.Column("line_number", sa.String(), nullable=False),
        sa.Column("pipe_size", sa.String(), nullable=False),
        sa.Column("spec", sa.String(), nullable=False),
        sa.Column("from_equipment", sa.String(), nullable=True),
        sa.Column("to_equipment", sa.String(), nullable=True),
        sa.Column("fluid", sa.String(), nullable=True),
        sa.Column(
            "validation_status",
            sa.Enum("pending", "valid", "mismatch", name="validationstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("mismatch_fields", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_line_list_entries_batch_id", "line_list_entries", ["batch_id"])
    op.create_index("ix_line_list_entries_line_number", "line_list_entries", ["line_number"])

    # pms_entries
    op.create_table(
        "pms_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", sa.String(), nullable=False),
        sa.Column("spec_code", sa.String(), nullable=False),
        sa.Column("material", sa.String(), nullable=False),
        sa.Column("rating", sa.String(), nullable=False),
        sa.Column("size_range", sa.String(), nullable=True),
        sa.Column("end_conn", sa.String(), nullable=True),
        sa.Column(
            "validation_status",
            sa.Enum("pending", "valid", "mismatch", name="pmsvalidationstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_pms_entries_batch_id", "pms_entries", ["batch_id"])
    op.create_index("ix_pms_entries_spec_code", "pms_entries", ["spec_code"])

    # validation_results
    op.create_table(
        "validation_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("iso_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iso_drawings.id"), nullable=False),
        sa.Column("line_list_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("line_list_entries.id"), nullable=True),
        sa.Column("pms_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pms_entries.id"), nullable=True),
        sa.Column("rule_name", sa.String(), nullable=False),
        sa.Column(
            "result",
            sa.Enum("pass", "fail", "warning", name="ruleresult"),
            nullable=False,
        ),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("validation_results")
    op.drop_table("pms_entries")
    op.drop_table("line_list_entries")
    op.drop_table("iso_drawings")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS ruleresult")
    op.execute("DROP TYPE IF EXISTS pmsvalidationstatus")
    op.execute("DROP TYPE IF EXISTS validationstatus")
    op.execute("DROP TYPE IF EXISTS isostatus")
    op.execute("DROP TYPE IF EXISTS userrole")
