from app.services.booking_service import cancel_appointment, reschedule_appointment
from app.services.security_service import create_signed_token, verify_signed_token

ACTION_TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60


def build_action_links(appointment_id: int):
    cancel_token = create_signed_token(
        {"type": "appointment_action", "action": "cancel", "appointment_id": appointment_id},
        ttl_seconds=ACTION_TOKEN_TTL_SECONDS,
    )
    reschedule_token = create_signed_token(
        {"type": "appointment_action", "action": "reschedule", "appointment_id": appointment_id},
        ttl_seconds=ACTION_TOKEN_TTL_SECONDS,
    )
    return {
        "cancel_token": cancel_token,
        "reschedule_token": reschedule_token,
    }


def apply_appointment_action(db, token: str, new_date: str = None, new_time: str = None):
    payload = verify_signed_token(token)
    if not payload or payload.get("type") != "appointment_action":
        return {"error": "Invalid or expired appointment action token"}

    appointment_id = payload.get("appointment_id")
    action = payload.get("action")
    if action == "cancel":
        return cancel_appointment(db, appointment_id)
    if action == "reschedule":
        if not new_time:
            return {"error": "new_time is required for reschedule"}
        return reschedule_appointment(db, appointment_id, new_time, new_date=new_date)
    return {"error": "Unsupported appointment action"}
