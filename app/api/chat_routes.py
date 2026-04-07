from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.conversation_service import handle_conversation

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/chat")
def chat(data: dict, db: Session = Depends(get_db)):
    session_id = data.get("session_id")
    text = data.get("text")

    return handle_conversation(session_id, text, db)