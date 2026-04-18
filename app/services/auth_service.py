from app.db.models import User
from app.services.security_service import create_signed_token, hash_password, verify_password, verify_signed_token

VALID_ROLES = {"admin", "analyst", "doctor", "patient", "receptionist"}


def register_user(db, name: str, email: str, password: str, role: str = "patient", allow_staff_roles: bool = False):
    normalized_role = role.strip().lower()
    if normalized_role not in VALID_ROLES:
        return {"error": "Invalid role"}

    has_users = db.query(User).first() is not None
    if has_users and normalized_role != "patient" and not allow_staff_roles:
        return {"error": "Staff users must be created by an admin"}

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {"error": "User already exists"}

    user = User(
        name=name,
        email=email,
        role=normalized_role,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _auth_response(user)


def authenticate_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return {"error": "Invalid email or password"}
    return _auth_response(user)


def get_user_from_token(db, token: str):
    payload = verify_signed_token(token)
    if not payload or payload.get("type") != "auth":
        return None
    return db.query(User).filter(User.id == payload.get("sub"), User.is_active == True).first()


def _auth_response(user):
    token = create_signed_token({
        "type": "auth",
        "sub": user.id,
        "email": user.email,
        "role": user.role,
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }
