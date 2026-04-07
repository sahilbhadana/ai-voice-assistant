sessions = {}


def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {
            "intent": None,
            "doctor_specialization": None,
            "time": None
        }
    return sessions[session_id]


def update_session(session_id, new_data):
    session = get_session(session_id)

    for key in ["intent", "doctor_specialization", "time"]:
        value = new_data.get(key)

        # Only update if value is not None
        if value is not None:
            session[key] = value

    return session


def clear_session(session_id):
    if session_id in sessions:
        del sessions[session_id]