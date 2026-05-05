from __future__ import annotations

from datetime import datetime, timedelta, timezone

from config import ADMIN_EMAIL, ADMIN_PASSWORD
from database import get_connection
from schemas import ContactSubmissionCreate
from security import (
    create_signed_session_token,
    generate_salt,
    hash_password,
    verify_password,
    verify_signed_session_token,
)


SESSION_DURATION = timedelta(days=7)


def ensure_admin_user() -> None:
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        return

    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, password_hash, password_salt FROM admin_users WHERE email = ?",
            (ADMIN_EMAIL,),
        ).fetchone()

        if row:
            return

        salt = generate_salt()
        password_hash = hash_password(ADMIN_PASSWORD, salt)
        connection.execute(
            "INSERT INTO admin_users (email, password_hash, password_salt) VALUES (?, ?, ?)",
            (ADMIN_EMAIL, password_hash, salt),
        )


def delete_expired_sessions() -> None:
    return None


def authenticate_admin(email: str, password: str) -> tuple[dict[str, str | int], str, str] | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, email, password_hash, password_salt FROM admin_users WHERE email = ?",
            (email,),
        ).fetchone()

    if not row:
        return None

    if not verify_password(password, row["password_salt"], row["password_hash"]):
        return None

    expires_at = (datetime.now(timezone.utc) + SESSION_DURATION).isoformat().replace(
        "+00:00", "Z"
    )
    admin = {"id": row["id"], "email": row["email"]}
    session_token = create_signed_session_token(
        user_id=row["id"],
        email=row["email"],
        expires_at=expires_at,
    )
    return admin, session_token, expires_at


def get_admin_by_session(session_token: str) -> dict[str, str | int] | None:
    return verify_signed_session_token(session_token)


def invalidate_session(session_token: str) -> None:
    return None


def save_contact_submission(payload: ContactSubmissionCreate) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO contact_submissions (name, email, company, message, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name.strip(),
                payload.email.strip().lower(),
                payload.company.strip() if payload.company else None,
                payload.message.strip(),
                payload.ip_address.strip() if payload.ip_address else None,
                payload.user_agent.strip() if payload.user_agent else None,
            ),
        )


def list_contact_submissions() -> list[dict[str, str | int | None]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, email, company, message, submitted_at, ip_address, user_agent
            FROM contact_submissions
            ORDER BY datetime(submitted_at) DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
