from __future__ import annotations

import base64
import json
import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from config import SESSION_SECRET


def hash_password(password: str, salt: str) -> str:
    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt.encode("utf-8"),
        n=16384,
        r=8,
        p=1,
        dklen=64,
    )
    return password_hash.hex()


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    incoming_hash = hash_password(password, salt)
    return hmac.compare_digest(incoming_hash, password_hash)


def generate_salt() -> str:
    return secrets.token_hex(16)


def generate_session_token() -> str:
    return secrets.token_hex(32)


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("utf-8"))


def create_signed_session_token(*, user_id: int, email: str, expires_at: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "expires_at": expires_at,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"), payload_bytes, hashlib.sha256
    ).digest()
    return f"{_encode(payload_bytes)}.{_encode(signature)}"


def verify_signed_session_token(token: str) -> dict[str, str | int] | None:
    try:
        payload_part, signature_part = token.split(".", 1)
        payload_bytes = _decode(payload_part)
        provided_signature = _decode(signature_part)
    except (ValueError, json.JSONDecodeError):
        return None

    expected_signature = hmac.new(
        SESSION_SECRET.encode("utf-8"), payload_bytes, hashlib.sha256
    ).digest()

    if not hmac.compare_digest(provided_signature, expected_signature):
        return None

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
        expires_at = datetime.fromisoformat(str(payload["expires_at"]).replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None

    if expires_at <= datetime.now(timezone.utc):
        return None

    return {
        "id": int(payload["user_id"]),
        "email": str(payload["email"]),
    }
