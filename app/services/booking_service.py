from sqlalchemy.orm import Session
from app.db.models import Doctor, Slot, Appointment, Patient
from sqlalchemy import func
from datetime import datetime, timedelta

def book_appointment(db: Session, patient_name: str, patient_email: str, specialization: str, time: str):
    """
    Book an appointment for a patient.
    
    Args:
        db: Database session
        patient_name: Name of patient
        patient_email: Email of patient
        specialization: Doctor specialization
        time: Appointment time (HH:MM)
    
    Returns:
        Dictionary with appointment details or error
    """

    # Step 1: Get or create patient
    patient = db.query(Patient).filter(Patient.email == patient_email).first()
    
    if not patient:
        patient = Patient(
            name=patient_name,
            email=patient_email,
            phone="N/A"  # Phone would be captured from caller ID in real system
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # Step 2: Find doctor
    doctor = db.query(Doctor).filter(
        func.lower(Doctor.specialization) == specialization.lower()
    ).first()

    if not doctor:
        return {"error": "No doctor found"}

    # Step 3: Find available slot
    slot = db.query(Slot).filter(
        Slot.doctor_id == doctor.id,
        Slot.time == time,
        Slot.is_available == True
    ).first()

    if not slot:
        return {"error": "No slot available"}

    # Step 4: Mark slot as unavailable
    slot.is_available = False

    # Step 5: Create appointment (assuming today's date + some days ahead)
    # In real system, this would be based on selected date
    appointment_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    appointment = Appointment(
        patient_id=patient.id,
        patient_name=patient_name,
        patient_email=patient_email,
        doctor_id=doctor.id,
        doctor_name=doctor.name,
        slot_id=slot.id,
        appointment_date=appointment_date,
        appointment_time=time,
        status="booked",
        email_sent=False
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment booked",
        "appointment_id": f"APT-{appointment.id}",
        "appointment": {
            "id": appointment.id,
            "doctor_name": doctor.name,
            "appointment_date": appointment_date,
            "appointment_time": time,
            "status": "booked"
        }
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