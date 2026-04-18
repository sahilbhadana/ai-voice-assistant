from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.database import SessionLocal
from app.services.auth_service import get_user_from_token

ROLE_ADMIN = "admin"
ROLE_ANALYST = "analyst"
ROLE_DOCTOR = "doctor"
ROLE_PATIENT = "patient"
ROLE_RECEPTIONIST = "receptionist"

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    db = SessionLocal()
    try:
        user = get_user_from_token(db, credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user
    finally:
        db.close()


def require_roles(*allowed_roles):
    def dependency(user=Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role permissions")
        return user

    return dependency
