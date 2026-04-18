from fastapi import Header, HTTPException

ROLE_ADMIN = "admin"
ROLE_ANALYST = "analyst"
ROLE_DOCTOR = "doctor"
ROLE_PATIENT = "patient"
ROLE_RECEPTIONIST = "receptionist"


def require_roles(*allowed_roles):
    def dependency(x_user_role: str = Header(default=ROLE_PATIENT)):
        role = x_user_role.strip().lower()
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role permissions")
        return role

    return dependency
