from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
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