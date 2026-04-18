from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.booking import BookingRequest, CancelRequest, RescheduleRequest, HistoryRequest
from app.services.booking_service import (
    book_appointment,
    get_available_slots,
    get_doctor_availability,
    get_appointment_history,
    cancel_appointment,
    reschedule_appointment
)

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
        req.time
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
def history(req: HistoryRequest, db: Session = Depends(get_db)):
    return {"appointments": get_appointment_history(db, req.patient_email)}


@router.post("/cancel")
def cancel(req: CancelRequest, db: Session = Depends(get_db)):
    result = cancel_appointment(db, req.appointment_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/reschedule")
def reschedule(req: RescheduleRequest, db: Session = Depends(get_db)):
    result = reschedule_appointment(db, req.appointment_id, req.new_time)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/slots")
def slots(specialization: str = Query(...), db: Session = Depends(get_db)):
    return {"available_slots": get_available_slots(db, specialization)}