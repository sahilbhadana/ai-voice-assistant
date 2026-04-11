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

def get_available_slots(db, specialization, time_preference=None):
    doctor = db.query(Doctor).filter(
        func.lower(Doctor.specialization) == specialization.lower()
    ).first()

    if not doctor:
        return []

    slots = db.query(Slot).filter(
        Slot.doctor_id == doctor.id,
        Slot.is_available == True
    ).all()

    slot_times = [slot.time for slot in slots]
    
    # Filter based on time preference
    if time_preference:
        slot_times = filter_slots_by_preference(slot_times, time_preference)
    
    return slot_times


def filter_slots_by_preference(slots, time_preference):
    """
    Filter slots based on user's time preference.
    
    Args:
        slots: List of time strings (e.g., ["09:00", "10:00", "14:00"])
        time_preference: "earliest_available", "any_time", "morning", "afternoon"
    
    Returns:
        Filtered list of slots
    """
    if time_preference == "earliest_available":
        # Return just the earliest slot
        return [slots[0]] if slots else []
    
    elif time_preference == "any_time":
        # Return all slots
        return slots
    
    elif time_preference == "morning":
        # Filter for 6:00 - 12:00
        return [s for s in slots if 6 <= int(s.split(":")[0]) < 12]
    
    elif time_preference == "afternoon":
        # Filter for 12:00 - 18:00
        return [s for s in slots if 12 <= int(s.split(":")[0]) < 18]
    
    return slots