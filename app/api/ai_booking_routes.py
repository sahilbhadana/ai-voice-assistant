from fastapi import APIRouter, Depends
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

    # Step 1: Extract structured data using LLM
    extracted = extract_intent(text)

    if "error" in extracted:
        return {"error": "Failed to extract intent", "details": extracted}

    # Step 2: Call booking logic
    result = book_appointment(
        db,
        patient_name="AI User",
        specialization=extracted.get("doctor_specialization"),
        time=extracted.get("time")
    )

    # Step 3: Return full pipeline result
    return {
        "input": text,
        "extracted": extracted,
        "booking_result": result
    }