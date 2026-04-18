"""operational hardening

Revision ID: 20260418_2215
Revises:
Create Date: 2026-04-18 22:15:00
"""
from alembic import op
import sqlalchemy as sa

revision = "20260418_2215"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "consent_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id")),
        sa.Column("consent_type", sa.String(), nullable=True),
        sa.Column("granted", sa.Boolean(), nullable=True),
        sa.Column("captured_by", sa.String(), nullable=True),
        sa.Column("captured_at", sa.DateTime(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "integration_sync_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("appointment_id", sa.Integer(), sa.ForeignKey("appointments.id")),
        sa.Column("target_system", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("external_reference", sa.String(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=True),
        sa.Column("next_retry_at", sa.DateTime(), nullable=True),
        sa.Column("synced_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("actor_email", sa.String(), nullable=True),
        sa.Column("actor_role", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=True),
        sa.Column("resource_type", sa.String(), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.add_column("appointments", sa.Column("external_ehr_id", sa.String(), nullable=True))
    op.add_column("appointments", sa.Column("external_calendar_id", sa.String(), nullable=True))


def downgrade():
    op.drop_column("appointments", "external_calendar_id")
    op.drop_column("appointments", "external_ehr_id")
    op.drop_table("audit_logs")
    op.drop_table("integration_sync_logs")
    op.drop_table("consent_records")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
