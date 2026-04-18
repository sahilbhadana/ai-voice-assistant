import ollama
import json
import re

def get_prompt_by_language(language: str, text: str) -> str:
    """Return the appropriate prompt based on language preference."""
    
    if language == "hi":
        # Hindi prompt
        prompt = f"""
        आप एक अस्पताल बुकिंग के लिए AI सहायक हैं।

        सख्त निर्देश:
        - आप केवल मान्य JSON वापस कर सकते हैं
        - कोई स्पष्टीकरण न जोड़ें
        - JSON के बाहर कोई टेक्स्ट न जोड़ें
        - मार्कडाउन के रूप में न फॉर्मेट करें

        JSON में ये कुंजी वापस करें:
        - intent
        - doctor_specialization
        - time_preference (इनमें से एक: "earliest_available", "any_time", "morning", "afternoon", null)
        - time

        अगर मूल्य गायब है तो null इस्तेमाल करें

        उदाहरण:

        इनपुट: अपॉइंटमेंट बुक करें
        आउटपुट:
        {{"intent": "book_appointment", "doctor_specialization": null, "time_preference": null, "time": null}}

        इनपुट: कार्डियोलॉजिस्ट
        आउटपुट:
        {{"intent": null, "doctor_specialization": "cardiologist", "time_preference": null, "time": null}}

        इनपुट: सुबह
        आउटपुट:
        {{"intent": null, "doctor_specialization": null, "time_preference": "morning", "time": null}}

        इनपुट: सबसे पहले उपलब्ध
        आउटपुट:
        {{"intent": null, "doctor_specialization": null, "time_preference": "earliest_available", "time": null}}

        इनपुट: 10 बजे
        आउटपुट:
        {{"intent": null, "doctor_specialization": null, "time_preference": null, "time": "10:00"}}

        अब इस से निकालें:
        {text}
        """
    else:
        # English prompt (default)
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
        - time_preference (one of: "earliest_available", "any_time", "morning", "afternoon", null)
        - time

        If value is missing, use null

        Examples:

        Input: Book appointment
        Output:
        {{"intent": "book_appointment", "doctor_specialization": null, "time_preference": null, "time": null}}

        Input: Cardiologist
        Output:
        {{"intent": null, "doctor_specialization": "cardiologist", "time_preference": null, "time": null}}

        Input: Morning
        Output:
        {{"intent": null, "doctor_specialization": null, "time_preference": "morning", "time": null}}

        Input: Earliest available
        Output:
        {{"intent": null, "doctor_specialization": null, "time_preference": "earliest_available", "time": null}}

        Input: 10 AM
        Output:
        {{"intent": null, "doctor_specialization": null, "time_preference": null, "time": "10:00"}}

        Now extract from:
        {text}
        """
    
    return prompt

def extract_intent(text: str, language: str = "en"):
    prompt = get_prompt_by_language(language, text)

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