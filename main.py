from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from database import initialize_database
from repository import (
    authenticate_admin,
    delete_expired_sessions,
    ensure_admin_user,
    get_admin_by_session,
    invalidate_session,
    list_contact_submissions,
    save_contact_submission,
)
from schemas import (
    AdminLoginRequest,
    AdminSessionResponse,
    AuthenticatedAdmin,
    ContactSubmissionCreate,
    ContactSubmissionRead,
    MessageResponse,
    SessionTokenRequest,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    ensure_admin_user()
    delete_expired_sessions()
    yield


app = FastAPI(
    title="Portfolio Backend",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=MessageResponse)
async def healthcheck() -> MessageResponse:
    return MessageResponse(message="ok")


@app.post("/api/contact", response_model=MessageResponse)
async def create_contact_submission(payload: ContactSubmissionCreate) -> MessageResponse:
    if not payload.name.strip() or not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name, email, and message are required.",
        )

    save_contact_submission(payload)
    return MessageResponse(message="Message sent successfully. Priyanshu will contact you soon.")


@app.post("/api/admin/login", response_model=AdminSessionResponse)
async def login(payload: AdminLoginRequest) -> AdminSessionResponse:
    admin_session = authenticate_admin(payload.email.strip().lower(), payload.password)

    if not admin_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
        )

    admin, session_token, expires_at = admin_session
    return AdminSessionResponse(
        session_token=session_token,
        expires_at=expires_at,
        admin=admin,
    )


@app.post("/api/admin/logout", response_model=MessageResponse)
async def logout(payload: SessionTokenRequest) -> MessageResponse:
    invalidate_session(payload.session_token)
    return MessageResponse(message="Logged out")


@app.post("/api/admin/session", response_model=AuthenticatedAdmin)
async def get_session(payload: SessionTokenRequest) -> AuthenticatedAdmin:
    admin = get_admin_by_session(payload.session_token)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session.",
        )

    return AuthenticatedAdmin(**admin)


@app.post("/api/admin/submissions", response_model=list[ContactSubmissionRead])
async def get_submissions(payload: SessionTokenRequest) -> list[ContactSubmissionRead]:
    admin = get_admin_by_session(payload.session_token)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session.",
        )

    return [ContactSubmissionRead(**item) for item in list_contact_submissions()]
