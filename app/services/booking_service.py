from sqlalchemy.orm import Session
from app.db.models import Doctor, Slot, Appointment

def book_appointment(db: Session, patient_name: str, specialization: str, time: str):
    
    doctor = db.query(Doctor).filter(
        Doctor.specialization == specialization
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