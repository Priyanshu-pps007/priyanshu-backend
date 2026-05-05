from __future__ import annotations

from pydantic import BaseModel, EmailStr


class ContactSubmissionCreate(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    message: str
    ip_address: str | None = None
    user_agent: str | None = None


class ContactSubmissionRead(BaseModel):
    id: int
    name: str
    email: str
    company: str | None
    message: str
    submitted_at: str
    ip_address: str | None
    user_agent: str | None


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminSessionResponse(BaseModel):
    session_token: str
    expires_at: str
    admin: dict[str, str | int]


class SessionTokenRequest(BaseModel):
    session_token: str


class AuthenticatedAdmin(BaseModel):
    id: int
    email: str


class MessageResponse(BaseModel):
    message: str

