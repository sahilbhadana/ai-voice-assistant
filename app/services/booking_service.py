from sqlalchemy.orm import Session
from app.db.models import Doctor, Slot, Appointment
from sqlalchemy import func

def book_appointment(db: Session, patient_name: str, specialization: str, time: str):

    doctor = db.query(Doctor).filter(
        func.lower(Doctor.specialization) == specialization.lower()
    ).first()

    if not doctor:
        return {"error": "No doctor found"}

    slot = db.query(Slot).filter(
        Slot.doctor_id == doctor.id,
        Slot.time == time,
        Slot.is_available == True
    ).first()

    if not slot:
        return {"error": "No slot available"}

    # Book slot
    slot.is_available = False

    appointment = Appointment(
        patient_name=patient_name,
        doctor_id=doctor.id,
        slot_id=slot.id
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment booked",
        "appointment_id": appointment.id
    }

def get_available_slots(db, specialization):
    doctor = db.query(Doctor).filter(
        func.lower(Doctor.specialization) == specialization.lower()
    ).first()

    if not doctor:
        return []

    slots = db.query(Slot).filter(
        Slot.doctor_id == doctor.id,
        Slot.is_available == True
    ).all()

    return [slot.time for slot in slots]