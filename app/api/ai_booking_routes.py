from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.llm_service import extract_intent
from app.services.booking_service import book_appointment

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ai/book")
def ai_book(data: dict, db: Session = Depends(get_db)):
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text input")

    extracted = extract_intent(text)
    if "error" in extracted:
        raise HTTPException(status_code=400, detail={"error": "Failed to extract intent", "details": extracted})

    result = book_appointment(
        db,
        patient_name="AI User",
        patient_email="ai-user@example.com",
        specialization=extracted.get("doctor_specialization"),
        time=extracted.get("time")
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "input": text,
        "extracted": extracted,
        "booking_result": result
    }