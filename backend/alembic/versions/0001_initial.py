"""initial: users / tasks / submissions / upload_files

Revision ID: 0001
Revises:
Create Date: 2026-11-06
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("emp_no", sa.String(32), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("group_name", sa.String(32), server_default=""),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("requirement", sa.Text(), server_default=""),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("assignee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("creator_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reject_reason", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "upload_files",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("submission_id", sa.Integer(), sa.ForeignKey("submissions.id"), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("stored_name", sa.String(255), nullable=False),
        sa.Column("size_bytes", sa.Float(), server_default="0"),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("upload_files")
    op.drop_table("submissions")
    op.drop_table("tasks")
    op.drop_table("users")
