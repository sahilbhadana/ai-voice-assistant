import ollama
import json
import re

def extract_intent(text: str):
    prompt = f"""
    You are an AI assistant for hospital booking.

    Extract structured JSON from user input.

    Return ONLY valid JSON. No explanation.

    Fields:
    - intent (always "book_appointment")
    - doctor_specialization (cardiologist, dermatologist, etc.)
    - time (HH:MM format)

    Example:
    Input: "Book cardiologist at 10"
    Output:
    {{
        "intent": "book_appointment",
        "doctor_specialization": "cardiologist",
        "time": "10:00"
    }}

    Input: "{text}"
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["message"]["content"]

    # Extract JSON safely
    match = re.search(r"\{.*\}", content, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            return {"error": "Invalid JSON from LLM"}

    return {"error": "No JSON found"}