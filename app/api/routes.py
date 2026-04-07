from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.booking import BookingRequest
from app.services.booking_service import book_appointment

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/book")
def book(req: BookingRequest, db: Session = Depends(get_db)):
    return book_appointment(
        db,
        req.patient_name,
        req.doctor_specialization,
        req.time
    )