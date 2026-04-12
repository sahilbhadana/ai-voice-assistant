from app.services.llm_service import extract_intent
from app.services.state_manager import get_session, update_session, clear_session
from app.services.booking_service import book_appointment, get_available_slots
from app.services.email_service import send_booking_confirmation
from app.db.models import Patient
from datetime import datetime


def handle_conversation(session_id, text, db):

    # Step 1: Extract structured data from user input
    extracted = extract_intent(text)
    print("EXTRACTED:", extracted)

    # Step 2: Get or create session
    session = get_session(session_id)

    # Step 2a: Collect patient info if not already collected
    if not session.get("patient_name"):
        # First message - collect name
        session["patient_name"] = text.strip()
        update_session(session_id, {"patient_name": text.strip()})
        return {"response": "Thank you! What's your email address?"}

    if not session.get("patient_email"):
        # Second message - collect email
        patient_email = text.strip()
        if "@" not in patient_email:
            return {"response": "Please provide a valid email address."}
        
        session["patient_email"] = patient_email
        update_session(session_id, {"patient_email": patient_email})
        return {"response": "Great! Which doctor specialization do you need?"}

    # Step 2b: Normalize specialization
    if extracted.get("doctor_specialization"):
        extracted["doctor_specialization"] = extracted["doctor_specialization"].lower()

    # Step 3: Update session
    session = update_session(session_id, extracted)
    print("SESSION AFTER UPDATE:", session)

    # Handle suggested slots selection / approval
    user_input = text.strip().lower()
    if session.get("suggested_slots"):

        # Case 1: approval words
        if user_input in ["yes", "okay", "ok", "sure"]:
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
        return {"response": "Which doctor specialization do you need?"}

    # Ask for time preference if missing
    if not session.get("time_preference") and not session.get("time"):
        return {
            "response": "How would you like to choose your appointment time?",
            "options": ["earliest available", "any time", "morning", "afternoon"],
            "follow_up": "Or specify a specific time like '10 AM'"
        }

    # Ask for specific time if preference is set but time not selected
    if session.get("time_preference") and not session.get("time"):
        return {"response": "Please select a specific time or confirm a suggestion."}

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
                "response": f"{session['time']} is not available. Available slots: {', '.join(available_slots)}"
            }

        else:
            return {
                "response": "No slots available for this doctor."
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
                appointment_id=result.get("appointment_id")
            )

    # Step 8: Clear session after success
    clear_session(session_id)

    return {
        "response": "Your appointment is booked! A confirmation email has been sent to your address.",
        "booking_result": result
    }