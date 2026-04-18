from app.services.llm_service import extract_intent
from app.services.state_manager import get_session, update_session, clear_session
from app.services.booking_service import book_appointment, get_available_slots
from app.services.email_service import send_booking_confirmation
from app.db.models import Patient
from datetime import datetime


def get_response_text(language: str, key: str) -> str:
    """Get response text based on language preference."""

    responses = {
        "en": {
            "language_selection": "Please select your language:\n1. English\n2. हिंदी (Hindi)",
            "invalid_language": "Please select 1 for English or 2 for Hindi.",
            "name_prompt": "Thank you! What's your name?",
            "email_prompt": "Thank you! What's your email address?",
            "invalid_email": "Please provide a valid email address.",
            "specialization_prompt": "Great! Which doctor specialization do you need?",
            "time_preference_prompt": "How would you like to choose your appointment time?",
            "time_options": ["earliest available", "any time", "morning", "afternoon"],
            "time_follow_up": "Or specify a specific time like '10 AM'",
            "time_selection_prompt": "Please select a specific time or confirm a suggestion.",
            "slot_unavailable": "is not available. Available slots:",
            "no_slots": "No slots available for this doctor.",
            "booking_success": "Your appointment is booked! A confirmation email has been sent to your address.",
            "booking_error": "Sorry, there was an error booking your appointment."
        },
        "hi": {
            "language_selection": "कृपया अपनी भाषा चुनें:\n1. English\n2. हिंदी",
            "invalid_language": "कृपया अंग्रेजी के लिए 1 या हिंदी के लिए 2 चुनें।",
            "name_prompt": "धन्यवाद! आपका नाम क्या है?",
            "email_prompt": "धन्यवाद! आपका ईमेल पता क्या है?",
            "invalid_email": "कृपया एक वैध ईमेल पता प्रदान करें।",
            "specialization_prompt": "बेहतरीन! आपको किस डॉक्टर की विशेषज्ञता चाहिए?",
            "time_preference_prompt": "आप अपना अपॉइंटमेंट समय कैसे चुनना चाहेंगे?",
            "time_options": ["सबसे पहले उपलब्ध", "कोई भी समय", "सुबह", "दोपहर"],
            "time_follow_up": "या '10 बजे' जैसे विशिष्ट समय निर्दिष्ट करें",
            "time_selection_prompt": "कृपया एक विशिष्ट समय चुनें या सुझाव की पुष्टि करें।",
            "slot_unavailable": "उपलब्ध नहीं है। उपलब्ध स्लॉट:",
            "no_slots": "इस डॉक्टर के लिए कोई स्लॉट उपलब्ध नहीं है।",
            "booking_success": "आपका अपॉइंटमेंट बुक हो गया है! आपके पते पर एक पुष्टिकरण ईमेल भेजा गया है।",
            "booking_error": "क्षमा करें, आपके अपॉइंटमेंट को बुक करने में त्रुटि हुई।"
        }
    }

    return responses.get(language, responses["en"]).get(key, "")


def handle_conversation(session_id, text, db):

    # Step 1: Get or create session
    session = get_session(session_id)

    # Step 1a: Language selection (first interaction)
    if not session.get("language"):
        # Check if user selected a language
        if text.strip() == "1":
            session["language"] = "en"
            update_session(session_id, {"language": "en"})
            return {"response": get_response_text("en", "name_prompt")}
        elif text.strip() == "2":
            session["language"] = "hi"
            update_session(session_id, {"language": "hi"})
            return {"response": get_response_text("hi", "name_prompt")}
        else:
            # First time or invalid selection
            return {"response": get_response_text("en", "language_selection")}

    # Get current language
    language = session.get("language", "en")

    # Step 2: Extract structured data from user input
    extracted = extract_intent(text, language)
    print("EXTRACTED:", extracted)

    # Step 2a: Collect patient info if not already collected
    if not session.get("patient_name"):
        # First message after language selection - collect name
        session["patient_name"] = text.strip()
        update_session(session_id, {"patient_name": text.strip()})
        return {"response": get_response_text(language, "email_prompt")}

    if not session.get("patient_email"):
        # Second message - collect email
        patient_email = text.strip()
        if "@" not in patient_email:
            return {"response": get_response_text(language, "invalid_email")}

        session["patient_email"] = patient_email
        update_session(session_id, {"patient_email": patient_email})
        return {"response": get_response_text(language, "specialization_prompt")}

    # Step 2b: Normalize specialization
    if extracted.get("doctor_specialization"):
        extracted["doctor_specialization"] = extracted["doctor_specialization"].lower()

    # Step 3: Update session
    session = update_session(session_id, extracted)
    print("SESSION AFTER UPDATE:", session)

    # Handle suggested slots selection / approval
    user_input = text.strip().lower()
    if session.get("suggested_slots"):

        # Case 1: approval words (handle both languages)
        approval_words = ["yes", "okay", "ok", "sure", "हाँ", "ठीक", "ओके", "निश्चित"]
        if user_input in approval_words:
            chosen_slot = session["suggested_slots"][0]
            session["time"] = chosen_slot
            session["suggested_slots"] = None

        else:
            # Case 2: user selects slot (like "12")
            for slot in session["suggested_slots"]:
                if user_input in slot:
                    session["time"] = slot
                    session["suggested_slots"] = None
                    break

    # Step 4: Decision Engine

    # Ask for doctor if missing
    if not session.get("doctor_specialization"):
        return {"response": get_response_text(language, "specialization_prompt")}

    # Ask for time preference if missing
    if not session.get("time_preference") and not session.get("time"):
        return {
            "response": get_response_text(language, "time_preference_prompt"),
            "options": get_response_text(language, "time_options"),
            "follow_up": get_response_text(language, "time_follow_up")
        }

    # Ask for specific time if preference is set but time not selected
    if session.get("time_preference") and not session.get("time"):
        return {"response": get_response_text(language, "time_selection_prompt")}

    # Step 5: Booking
    result = book_appointment(
        db,
        patient_name=session["patient_name"],
        patient_email=session["patient_email"],
        specialization=session["doctor_specialization"],
        time=session["time"]
    )

    # Step 6: Handle booking result properly (IMPORTANT FIX)
    if "error" in result:

        available_slots = get_available_slots(
            db,
            session["doctor_specialization"],
            session.get("time_preference")
        )

        if available_slots:
            session["suggested_slots"] = available_slots

            return {
                "response": f"{session['time']} {get_response_text(language, 'slot_unavailable')} {', '.join(available_slots)}"
            }

        else:
            return {
                "response": get_response_text(language, "no_slots")
            }

    # Step 7: Send confirmation email
    if result.get("appointment_id"):
        appointment = result.get("appointment")
        if appointment:
            send_booking_confirmation(
                patient_name=session["patient_name"],
                patient_email=session["patient_email"],
                doctor_name=appointment.get("doctor_name", "Dr. Name"),
                appointment_date=appointment.get("appointment_date", "TBD"),
                appointment_time=appointment.get("appointment_time", "TBD"),
                location="Room TBD",
                appointment_id=result.get("appointment_id"),
                language=language
            )

    # Step 8: Clear session after success
    clear_session(session_id)

    return {
        "response": get_response_text(language, "booking_success"),
        "booking_result": result
    }