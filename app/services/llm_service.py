import ollama
import json
import re

def extract_intent(text: str):
    prompt = f"""
        You are an AI assistant for hospital booking.

        STRICT INSTRUCTIONS:
        - You MUST return ONLY valid JSON
        - DO NOT include any explanation
        - DO NOT include text outside JSON
        - DO NOT format as markdown

        Return JSON with keys:
        - intent
        - doctor_specialization
        - time

        If value is missing, use null

        Examples:

        Input: Book appointment
        Output:
        {{"intent": "book_appointment", "doctor_specialization": null, "time": null}}

        Input: Cardiologist
        Output:
        {{"intent": null, "doctor_specialization": "cardiologist", "time": null}}

        Input: 10 AM
        Output:
        {{"intent": null, "doctor_specialization": null, "time": "10:00"}}

        Now extract from:
        {text}
        """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["message"]["content"]
    print("RAW LLM OUTPUT:", content)

    try:
        return json.loads(content)
    except:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return {"error": "Invalid JSON"}
        return {"error": "No JSON found"}