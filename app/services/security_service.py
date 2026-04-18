import base64
import hashlib
import hmac
import json
import os
import secrets
import time

SECRET_KEY = os.getenv("APP_SECRET_KEY", "change-this-secret-before-production")
TOKEN_TTL_SECONDS = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "86400"))


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, expected_digest = password_hash.split("$", 2)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return hmac.compare_digest(digest.hex(), expected_digest)


def create_signed_token(payload: dict, ttl_seconds: int = TOKEN_TTL_SECONDS) -> str:
    token_payload = {
        **payload,
        "exp": int(time.time()) + ttl_seconds,
    }
    body = _b64encode(json.dumps(token_payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = hmac.new(SECRET_KEY.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    return f"{body}.{_b64encode(signature)}"


def verify_signed_token(token: str):
    try:
        body, signature = token.split(".", 1)
        decoded_signature = _b64decode(signature)
    except ValueError:
        return None
    except Exception:
        return None

    expected_signature = hmac.new(SECRET_KEY.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    if not hmac.compare_digest(decoded_signature, expected_signature):
        return None

    try:
        payload = json.loads(_b64decode(body).decode("utf-8"))
    except Exception:
        return None
    if payload.get("exp", 0) < int(time.time()):
        return None
    return payload
