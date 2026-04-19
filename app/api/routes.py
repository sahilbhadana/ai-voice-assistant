from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.booking import (
    AnalyticsRequest,
    AppointmentActionRequest,
    BookingRequest,
    CancelRequest,
    ConsentCaptureRequest,
    HistoryRequest,
    IntegrationSyncRequest,
    LoginRequest,
    RegisterRequest,
    RescheduleRequest,
    SessionLockRequest,
)
from app.services.appointment_action_service import apply_appointment_action
from app.services.audit_service import get_audit_logs, write_audit_log
from app.services.auth_service import authenticate_user, register_user
from app.services.booking_service import (
    book_appointment,
    get_available_slots,
    get_doctor_availability,
    get_appointment_history,
    cancel_appointment,
    reschedule_appointment,
    send_upcoming_sms_reminders
)
from app.services.access_control import get_current_user, require_roles
from app.services.analytics_service import get_demand_report
from app.services.consent_service import capture_consent, get_patient_consents
from app.services.integration_service import get_sync_history, retry_pending_syncs, sync_appointment
from app.services.state_manager import get_session_lock, lock_session, unlock_session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/book")
def book(
    req: BookingRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist", "patient"))
):
    if user.role == "patient" and req.patient_email.lower() != user.email.lower():
        raise HTTPException(status_code=403, detail="Patients can only book appointments for their own account")
    try:
        result = book_appointment(
            db,
            req.patient_name,
            req.patient_email,
            req.doctor_specialization,
            req.time,
            patient_phone=req.patient_phone,
            consent_granted=req.consent_granted,
            consent_notes=req.consent_notes,
            date=req.date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    write_audit_log(db, user, "book_appointment", "appointment", result["appointment"]["id"])
    return result


@router.get("/availability")
def availability(specialization: str = Query(...), date: str = Query(None), db: Session = Depends(get_db)):
    try:
        result = get_doctor_availability(db, specialization, date=date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    result = register_user(db, req.name, req.email, req.password, req.role)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/auth/users")
def create_user(
    req: RegisterRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin"))
):
    result = register_user(db, req.name, req.email, req.password, req.role, allow_staff_roles=True)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    write_audit_log(db, user, "create_user", "user", result["user"]["id"], {"role": result["user"]["role"]})
    return result


@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    result = authenticate_user(db, req.email, req.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@router.get("/auth/me")
def me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


@router.post("/history")
def history(
    req: HistoryRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist", "doctor", "patient"))
):
    if user.role == "patient" and req.patient_email.lower() != user.email.lower():
        raise HTTPException(status_code=403, detail="Patients can only view their own appointment history")
    write_audit_log(db, user, "view_appointment_history", "patient", req.patient_email)
    return {"appointments": get_appointment_history(db, req.patient_email)}


@router.post("/cancel")
def cancel(
    req: CancelRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = cancel_appointment(db, req.appointment_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    write_audit_log(db, user, "cancel_appointment", "appointment", req.appointment_id)
    return result


@router.post("/reschedule")
def reschedule(
    req: RescheduleRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist", "doctor"))
):
    try:
        result = reschedule_appointment(db, req.appointment_id, req.new_time, new_date=req.new_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    write_audit_log(db, user, "reschedule_appointment", "appointment", req.appointment_id)
    return result


@router.get("/slots")
def slots(specialization: str = Query(...), date: str = Query(None), db: Session = Depends(get_db)):
    try:
        return {"available_slots": get_available_slots(db, specialization, date=date)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notifications/reminders")
def reminders(
    minutes_ahead: int = Query(1440, ge=1, description="Send reminders for appointments in the next X minutes"),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist"))
):
    results = send_upcoming_sms_reminders(db, minutes_ahead)
    write_audit_log(db, user, "send_sms_reminders", "notification", details={"minutes_ahead": minutes_ahead})
    return {
        "message": "SMS reminders dispatched",
        "reminders_sent": len(results),
        "details": results
    }


@router.post("/consents")
def consents(
    req: ConsentCaptureRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist", "doctor"))
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
    write_audit_log(db, user, "capture_consent", "patient", req.patient_email, {"consent_type": req.consent_type})
    return result


@router.get("/consents/{patient_email}")
def patient_consents(
    patient_email: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = get_patient_consents(db, patient_email)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    write_audit_log(db, user, "view_consents", "patient", patient_email)
    return result


@router.post("/sessions/lock")
def session_lock(
    req: SessionLockRequest,
    user=Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = lock_session(req.session_id, req.locked_by, req.reason)
    db = SessionLocal()
    try:
        write_audit_log(db, user, "lock_session", "session", req.session_id, {"reason": req.reason})
    finally:
        db.close()
    return result


@router.post("/sessions/{session_id}/unlock")
def session_unlock(
    session_id: str,
    user=Depends(require_roles("admin", "receptionist", "doctor"))
):
    result = unlock_session(session_id)
    db = SessionLocal()
    try:
        write_audit_log(db, user, "unlock_session", "session", session_id)
    finally:
        db.close()
    return result


@router.get("/sessions/{session_id}/lock")
def session_lock_status(
    session_id: str,
    user=Depends(require_roles("admin", "receptionist", "doctor"))
):
    return get_session_lock(session_id)


@router.post("/integrations/sync")
def integration_sync(
    req: IntegrationSyncRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist"))
):
    result = sync_appointment(db, req.appointment_id, req.target_system)
    if "error" in result:
        status_code = 404 if result["error"] == "Appointment not found" else 400
        raise HTTPException(status_code=status_code, detail=result["error"])
    write_audit_log(db, user, "sync_appointment", "appointment", req.appointment_id, {"target_system": req.target_system})
    return result


@router.get("/integrations/{appointment_id}/history")
def integration_history(
    appointment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist"))
):
    return get_sync_history(db, appointment_id)


@router.post("/integrations/retry")
def integration_retry(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "receptionist"))
):
    results = retry_pending_syncs(db, limit)
    write_audit_log(db, user, "retry_integration_syncs", "integration", details={"limit": limit})
    return {"retried": len(results), "details": results}


@router.post("/analytics/demand")
def analytics_demand(
    req: AnalyticsRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "analyst"))
):
    try:
        result = get_demand_report(db, req.start_date, req.end_date)
        write_audit_log(db, user, "view_demand_report", "analytics", details={"start_date": req.start_date, "end_date": req.end_date})
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Dates must use YYYY-MM-DD format")


@router.post("/appointments/action")
def appointment_action(req: AppointmentActionRequest, db: Session = Depends(get_db)):
    try:
        result = apply_appointment_action(db, req.token, req.new_date, req.new_time)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/appointments/cancel/{token}")
def appointment_cancel_link(token: str, db: Session = Depends(get_db)):
    result = apply_appointment_action(db, token)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/audit/logs")
def audit_logs(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin"))
):
    write_audit_log(db, user, "view_audit_logs", "audit", details={"limit": limit})
    return {"audit_logs": get_audit_logs(db, limit)}
