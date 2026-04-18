from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.booking import (
    AnalyticsRequest,
    BookingRequest,
    CancelRequest,
    ConsentCaptureRequest,
    HistoryRequest,
    IntegrationSyncRequest,
    RescheduleRequest,
    SessionLockRequest,
)
from app.services.booking_service import (
    book_appointment,
    get_available_slots,
    get_doctor_availability,
    get_appointment_history,
    cancel_appointment,
    reschedule_appointment,
    send_upcoming_sms_reminders
)
from app.services.access_control import require_roles
from app.services.analytics_service import get_demand_report
from app.services.consent_service import capture_consent, get_patient_consents
from app.services.integration_service import get_sync_history, sync_appointment
from app.services.state_manager import get_session_lock, lock_session, unlock_session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/book")
def book(req: BookingRequest, db: Session = Depends(get_db)):
    result = book_appointment(
        db,
        req.patient_name,
        req.patient_email,
        req.doctor_specialization,
        req.time,
        patient_phone=req.patient_phone,
        consent_granted=req.consent_granted,
        consent_notes=req.consent_notes
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/availability")
def availability(specialization: str = Query(...), db: Session = Depends(get_db)):
    result = get_doctor_availability(db, specialization)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/history")
def history(
    req: HistoryRequest,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist", "doctor", "patient"))
):
    return {"appointments": get_appointment_history(db, req.patient_email)}


@router.post("/cancel")
def cancel(
    req: CancelRequest,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = cancel_appointment(db, req.appointment_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/reschedule")
def reschedule(
    req: RescheduleRequest,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = reschedule_appointment(db, req.appointment_id, req.new_time)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/slots")
def slots(specialization: str = Query(...), db: Session = Depends(get_db)):
    return {"available_slots": get_available_slots(db, specialization)}


@router.post("/notifications/reminders")
def reminders(
    minutes_ahead: int = Query(1440, ge=1, description="Send reminders for appointments in the next X minutes"),
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist"))
):
    results = send_upcoming_sms_reminders(db, minutes_ahead)
    return {
        "message": "SMS reminders dispatched",
        "reminders_sent": len(results),
        "details": results
    }


@router.post("/consents")
def consents(
    req: ConsentCaptureRequest,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = capture_consent(
        db,
        patient_email=req.patient_email,
        consent_type=req.consent_type,
        granted=req.granted,
        captured_by=req.captured_by,
        source=req.source,
        notes=req.notes,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/consents/{patient_email}")
def patient_consents(
    patient_email: str,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = get_patient_consents(db, patient_email)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/sessions/lock")
def session_lock(
    req: SessionLockRequest,
    role: str = Depends(require_roles("admin", "receptionist", "doctor"))
):
    return lock_session(req.session_id, req.locked_by, req.reason)


@router.post("/sessions/{session_id}/unlock")
def session_unlock(
    session_id: str,
    role: str = Depends(require_roles("admin", "receptionist", "doctor"))
):
    return unlock_session(session_id)


@router.get("/sessions/{session_id}/lock")
def session_lock_status(
    session_id: str,
    role: str = Depends(require_roles("admin", "receptionist", "doctor"))
):
    return get_session_lock(session_id)


@router.post("/integrations/sync")
def integration_sync(
    req: IntegrationSyncRequest,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist"))
):
    result = sync_appointment(db, req.appointment_id, req.target_system)
    if "error" in result:
        status_code = 404 if result["error"] == "Appointment not found" else 400
        raise HTTPException(status_code=status_code, detail=result["error"])
    return result


@router.get("/integrations/{appointment_id}/history")
def integration_history(
    appointment_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "receptionist"))
):
    return get_sync_history(db, appointment_id)


@router.post("/analytics/demand")
def analytics_demand(
    req: AnalyticsRequest,
    db: Session = Depends(get_db),
    role: str = Depends(require_roles("admin", "analyst"))
):
    try:
        return get_demand_report(db, req.start_date, req.end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Dates must use YYYY-MM-DD format")
