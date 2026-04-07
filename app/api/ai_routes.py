from fastapi import APIRouter
from app.services.llm_service import extract_intent

router = APIRouter()

@router.post("/ai/extract")
def extract(data: dict):
    text = data.get("text")
    return extract_intent(text)