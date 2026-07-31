"""
Authentication Schemas.

Pydantic request/response models for the `/auth` endpoints, matching
the documented request/response shapes.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 4 - Authentication APIs)
"""

import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.core.security import validate_password_policy
from backend.models.enums import UserRole


class RegisterRequest(BaseModel):
    """Matches the documented Register Request exactly: name, email, password, role."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str
    role: UserRole

    @field_validator("password")
    @classmethod
    def _check_password_policy(cls, value: str) -> str:
        """Enforces the documented password policy at request-validation time."""
        validate_password_policy(value)
        return value


class UserPublic(BaseModel):
    """Public-safe representation of a User — never includes password_hash."""

    model_config = {"from_attributes": True}

    user_id: uuid.UUID
    name: str
    email: str
    role: UserRole


class LoginRequest(BaseModel):
    """Matches the documented Login Request exactly: email, password."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """
    Matches the documented Login Response (access_token, token_type,
    expires_in, role) plus `refresh_token`, added because Session
    Management (Security Architecture Section 8) requires refresh
    token support and login is the only point one can originate from.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    role: UserRole


class RefreshRequest(BaseModel):
    """Request body for POST /auth/refresh."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response for POST /auth/refresh — a new access token only; the
    original refresh token remains valid until its own expiry."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class LogoutResponse(BaseModel):
    """
    Response for POST /auth/logout.

    Server-side token revocation is explicitly documented as a future
    enhancement (Security Architecture Section 8), so logout is
    stateless: the client is instructed to discard both tokens.
    """

    message: str = "Logged out successfully. Please discard your access and refresh tokens."