"""add active appointment slot guard

Revision ID: 20260419_0100
Revises: 20260418_2215
Create Date: 2026-04-19 01:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "20260419_0100"
down_revision = "20260418_2215"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "uq_active_appointment_slot",
        "appointments",
        ["doctor_id", "appointment_date", "appointment_time"],
        unique=True,
        postgresql_where=sa.text("status IN ('booked', 'rescheduled')"),
    )


def downgrade():
    op.drop_index("uq_active_appointment_slot", table_name="appointments")
