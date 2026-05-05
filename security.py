from __future__ import annotations

import hashlib
import hmac
import secrets


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
