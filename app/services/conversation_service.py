from app.services.llm_service import extract_intent
from app.services.state_manager import get_session, update_session, clear_session
from app.services.booking_service import book_appointment, get_available_slots


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

        available_slots = get_available_slots(
            db,
            session["doctor_specialization"]
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

    # Step 7: Clear session after success
    clear_session(session_id)

    return {
        "response": "Your appointment is booked!",
        "booking_result": result
    }