from app.services.llm_service import extract_intent
from app.services.state_manager import get_session, update_session, clear_session
from app.services.booking_service import book_appointment


def handle_conversation(session_id, text, db):

    # Step 1: Extract structured data from user input
    extracted = extract_intent(text)
    print("EXTRACTED:", extracted)

    # Step 2: Normalize data (IMPORTANT)
    if extracted.get("doctor_specialization"):
        extracted["doctor_specialization"] = extracted["doctor_specialization"].lower()

    # Step 3: Update session
    session = update_session(session_id, extracted)
    print("SESSION AFTER UPDATE:", session)

    # Step 4: Decision Engine

    # Ask for doctor if missing
    if not session.get("doctor_specialization"):
        return {"response": "Which doctor specialization do you need?"}

    # Ask for time if missing
    if not session.get("time"):
        return {"response": "What time would you prefer?"}

    # Step 5: Booking
    result = book_appointment(
        db,
        patient_name="AI User",
        specialization=session["doctor_specialization"],
        time=session["time"]
    )

    # Step 6: Handle booking result properly (IMPORTANT FIX)
    if "error" in result:
        return {
            "response": f"Booking failed: {result['error']}"
        }

    # Step 7: Clear session after success
    clear_session(session_id)

    return {
        "response": "Your appointment is booked!",
        "booking_result": result
    }