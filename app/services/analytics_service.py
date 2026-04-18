from collections import Counter, defaultdict
from datetime import datetime

from app.db.models import Appointment, Doctor, Slot


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _in_range(appointment, start_date, end_date):
    appointment_date = _parse_date(appointment.appointment_date)
    if start_date and appointment_date < start_date:
        return False
    if end_date and appointment_date > end_date:
        return False
    return True


def get_demand_report(db, start_date: str = None, end_date: str = None):
    start = _parse_date(start_date)
    end = _parse_date(end_date)
    appointments = [
        appointment
        for appointment in db.query(Appointment).all()
        if _in_range(appointment, start, end)
    ]

    by_status = Counter(appointment.status for appointment in appointments)
    by_doctor = Counter(appointment.doctor_name for appointment in appointments)
    by_day = Counter(appointment.appointment_date for appointment in appointments)

    doctor_specializations = {
        doctor.id: doctor.specialization
        for doctor in db.query(Doctor).all()
    }
    by_specialization = Counter(
        doctor_specializations.get(appointment.doctor_id, "unknown")
        for appointment in appointments
    )

    slot_supply = defaultdict(lambda: {"total_slots": 0, "available_slots": 0})
    slots = db.query(Slot).all()
    for slot in slots:
        specialization = doctor_specializations.get(slot.doctor_id, "unknown")
        slot_supply[specialization]["total_slots"] += 1
        if slot.is_available:
            slot_supply[specialization]["available_slots"] += 1

    demand_by_specialization = []
    for specialization, booking_count in by_specialization.items():
        supply = slot_supply.get(specialization, {"total_slots": 0, "available_slots": 0})
        demand_by_specialization.append(
            {
                "specialization": specialization,
                "booked_appointments": booking_count,
                "total_slots": supply["total_slots"],
                "available_slots": supply["available_slots"],
                "utilization_percent": round(
                    (booking_count / supply["total_slots"]) * 100,
                    2,
                )
                if supply["total_slots"]
                else 0,
            }
        )

    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "total_appointments": len(appointments),
        "appointments_by_status": dict(by_status),
        "appointments_by_day": dict(sorted(by_day.items())),
        "appointments_by_doctor": dict(by_doctor),
        "demand_by_specialization": sorted(
            demand_by_specialization,
            key=lambda item: item["booked_appointments"],
            reverse=True,
        ),
    }
