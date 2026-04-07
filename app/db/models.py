from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .database import Base

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
    patient_name = Column(String)
    doctor_id = Column(Integer)
    slot_id = Column(Integer)
    status = Column(String, default="booked")