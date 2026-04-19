from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Index
from datetime import datetime
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="patient")
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialization = Column(String)


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    time = Column(String)
    is_available = Column(Boolean, default=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    patient_name = Column(String)
    patient_email = Column(String)
    doctor_id = Column(Integer)
    doctor_name = Column(String)
    slot_id = Column(Integer)
    appointment_date = Column(String)  # YYYY-MM-DD format
    appointment_time = Column(String)  # HH:MM format
    status = Column(String, default="booked")  # booked, completed, cancelled, no_show
    created_at = Column(DateTime, default=datetime.utcnow)
    email_sent = Column(Boolean, default=False)  # Track if confirmation email sent
    external_ehr_id = Column(String)
    external_calendar_id = Column(String)
    __table_args__ = (
        Index(
            "uq_active_appointment_slot",
            "doctor_id",
            "appointment_date",
            "appointment_time",
            unique=True,
            postgresql_where=status.in_(["booked", "rescheduled"]),
        ),
    )


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    consent_type = Column(String, default="booking_notifications")
    granted = Column(Boolean, default=False)
    captured_by = Column(String, default="system")
    captured_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String, default="api")
    notes = Column(Text)


class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    target_system = Column(String)
    status = Column(String)
    external_reference = Column(String)
    message = Column(Text)
    payload = Column(Text)
    attempts = Column(Integer, default=1)
    next_retry_at = Column(DateTime)
    synced_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"))
    actor_email = Column(String)
    actor_role = Column(String)
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
