from sqlalchemy.orm import Session
from app.db.models import Doctor, Slot, Appointment, Patient
from app.services.notification_service import send_sms, build_sms_message, build_reminder_message
from sqlalchemy import func
from datetime import datetime, timedelta

def book_appointment(db: Session, patient_name: str, patient_email: str, specialization: str, time: str, patient_phone: str = None, language: str = "en"):
    """
    Book an appointment for a patient.
    """
    patient = db.query(Patient).filter(Patient.email == patient_email).first()

    if not patient:
        patient = Patient(
            name=patient_name,
            email=patient_email,
            phone=patient_phone
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    else:
        if patient_phone and patient.phone in (None, "N/A", ""):
            patient.phone = patient_phone
            db.commit()
            db.refresh(patient)

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

    slot.is_available = False

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

    if patient.phone and patient.phone not in ("N/A", ""):
        sms_message = build_sms_message(
            patient_name=patient_name,
            doctor_name=doctor.name,
            appointment_date=appointment_date,
            appointment_time=time,
            appointment_id=f"APT-{appointment.id}",
            language=language
        )
        send_sms(patient.phone, sms_message)

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

    if time_preference:
        slot_times = filter_slots_by_preference(slot_times, time_preference)

    return slot_times


def get_doctor_availability(db, specialization):
    doctor = db.query(Doctor).filter(
        func.lower(Doctor.specialization) == specialization.lower()
    ).first()

    if not doctor:
        return {"error": "No doctor found"}

    slots = db.query(Slot).filter(
        Slot.doctor_id == doctor.id
    ).all()

    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "specialization": doctor.specialization,
        "slots": [
            {
                "time": slot.time,
                "is_available": slot.is_available
            }
            for slot in sorted(slots, key=lambda s: s.time)
        ]
    }


def _find_upcoming_appointments(db, minutes_ahead: int):
    now = datetime.now()
    cutoff = now + timedelta(minutes=minutes_ahead)
    appointments = db.query(Appointment).filter(Appointment.status == "booked").all()

    upcoming = []
    for appt in appointments:
        try:
            appointment_at = datetime.strptime(f"{appt.appointment_date} {appt.appointment_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        if now <= appointment_at <= cutoff:
            upcoming.append(appt)

    return upcoming


def send_upcoming_sms_reminders(db, minutes_ahead: int = 1440):
    appointments = _find_upcoming_appointments(db, minutes_ahead)
    results = []

    for appt in appointments:
        patient = db.query(Patient).filter(Patient.id == appt.patient_id).first()
        if not patient or not patient.phone or patient.phone in ("N/A", ""):
            continue

        message = build_reminder_message(
            patient_name=appt.patient_name,
            doctor_name=appt.doctor_name,
            appointment_date=appt.appointment_date,
            appointment_time=appt.appointment_time,
            appointment_id=f"APT-{appt.id}",
            hours_ahead=minutes_ahead // 60
        )
        sent = send_sms(patient.phone, message)
        results.append({
            "appointment_id": f"APT-{appt.id}",
            "patient_phone": patient.phone,
            "status": "sent" if sent else "failed"
        })

    return results


def get_appointment_history(db, patient_email: str):
    patient = db.query(Patient).filter(Patient.email == patient_email).first()
    if not patient:
        return []

    appointments = db.query(Appointment).filter(Appointment.patient_id == patient.id).order_by(Appointment.created_at.desc()).all()
    return [
        {
            "appointment_id": f"APT-{appt.id}",
            "doctor_name": appt.doctor_name,
            "appointment_date": appt.appointment_date,
            "appointment_time": appt.appointment_time,
            "status": appt.status,
            "created_at": appt.created_at.isoformat()
        }
        for appt in appointments
    ]


def cancel_appointment(db, appointment_id: int):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return {"error": "Appointment not found"}

    if appointment.status == "cancelled":
        return {"error": "Appointment already cancelled"}

    slot = db.query(Slot).filter(Slot.id == appointment.slot_id).first()
    if slot:
        slot.is_available = True

    appointment.status = "cancelled"
    db.commit()

    return {
        "message": "Appointment cancelled",
        "appointment_id": f"APT-{appointment.id}",
        "status": appointment.status
    }


def reschedule_appointment(db, appointment_id: int, new_time: str):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return {"error": "Appointment not found"}

    if appointment.status == "cancelled":
        return {"error": "Cancelled appointments cannot be rescheduled"}

    current_slot = db.query(Slot).filter(Slot.id == appointment.slot_id).first()
    new_slot = db.query(Slot).filter(
        Slot.doctor_id == appointment.doctor_id,
        Slot.time == new_time,
        Slot.is_available == True
    ).first()

    if not new_slot:
        return {"error": "Requested time slot is not available"}

    if current_slot:
        current_slot.is_available = True

    new_slot.is_available = False
    appointment.slot_id = new_slot.id
    appointment.appointment_time = new_time
    appointment.status = "rescheduled"
    db.commit()

    return {
        "message": "Appointment rescheduled",
        "appointment_id": f"APT-{appointment.id}",
        "appointment": {
            "doctor_name": appointment.doctor_name,
            "appointment_date": appointment.appointment_date,
            "appointment_time": new_time,
            "status": appointment.status
        }
    }


def filter_slots_by_preference(slots, time_preference):
    if time_preference == "earliest_available":
        return [slots[0]] if slots else []
    elif time_preference == "any_time":
        return slots
    elif time_preference == "morning":
        return [s for s in slots if 6 <= int(s.split(":")[0]) < 12]
    elif time_preference == "afternoon":
        return [s for s in slots if 12 <= int(s.split(":")[0]) < 18]
    return slots
