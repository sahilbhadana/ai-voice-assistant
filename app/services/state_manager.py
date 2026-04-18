sessions = {}
session_locks = {}


def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {
            "language": None,  # "en" for English, "hi" for Hindi
            "patient_name": None,
            "patient_email": None,
            "patient_phone": None,
            "intent": None,
            "doctor_specialization": None,
            "time_preference": None,
            "time": None,
            "suggested_slots": None
        }
    return sessions[session_id]


def update_session(session_id, new_data):
    if is_session_locked(session_id):
        return get_session(session_id)

    session = get_session(session_id)

    for key in ["language", "patient_name", "patient_email", "patient_phone", "intent", "doctor_specialization", "time_preference", "time", "suggested_slots"]:
        value = new_data.get(key)

        # Only update if value is not None
        if value is not None:
            session[key] = value

    return session


def clear_session(session_id):
    if is_session_locked(session_id):
        return

    if session_id in sessions:
        del sessions[session_id]


def lock_session(session_id, locked_by, reason=None):
    session_locks[session_id] = {
        "locked_by": locked_by,
        "reason": reason,
    }
    get_session(session_id)
    return {
        "session_id": session_id,
        "locked": True,
        "locked_by": locked_by,
        "reason": reason,
    }


def unlock_session(session_id):
    session_locks.pop(session_id, None)
    return {
        "session_id": session_id,
        "locked": False,
    }


def is_session_locked(session_id):
    return session_id in session_locks


def get_session_lock(session_id):
    lock = session_locks.get(session_id)
    return {
        "session_id": session_id,
        "locked": lock is not None,
        "locked_by": lock.get("locked_by") if lock else None,
        "reason": lock.get("reason") if lock else None,
    }
