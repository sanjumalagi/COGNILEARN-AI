"""
Security Module.

Provides the security primitives shared application-wide:

- `SecurityHeadersMiddleware` — secure-by-default HTTP response headers.
- Password hashing/verification/policy validation (bcrypt), per
  Security Architecture Sections 7 ("Password Security").
- JWT issuance and validation (`JWTService`), per Security Architecture
  Section 6 ("Authentication Architecture") and API Architecture
  Section 11 ("JWT Payload").

Role-Based Access Control (the `require_role` dependency) lives in
`core/dependencies.py` alongside `get_current_user`, since both are
FastAPI dependency-injection providers rather than stateless utilities.

Reference: 02_System_Architecture/06_Security_Architecture.md (Sections 6-9)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 11 - JWT Payload)
Reference: 01_Project_Foundation/05_Technology_Stack.md (Section 11)
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import bcrypt
import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.config import settings
from backend.core.exceptions import AuthenticationError, ValidationFailedError
from backend.models.enums import UserRole

# ----------------------------------------------------------------------
# Security Headers Middleware
# ----------------------------------------------------------------------


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds standard, secure-by-default HTTP response headers to every
    response, per the "Secure by Default" principle in the Security
    Architecture document.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers.setdefault("X-Cognilearn-Version", "1.0.0")
        return response


# ----------------------------------------------------------------------
# Password Security (Security Architecture, Section 7)
# ----------------------------------------------------------------------

# bcrypt only uses the first 72 bytes of the input; passwords longer than
# that are rejected outright rather than silently truncated.
_MAX_PASSWORD_BYTES = 72

_PASSWORD_POLICY_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
)


def validate_password_policy(password: str) -> None:
    """
    Enforces the documented password policy: minimum 8 characters, and
    at least one uppercase letter, one lowercase letter, one number,
    and one special character.

    Reference: 02_System_Architecture/06_Security_Architecture.md (Section 7 - Password Policy)
    """
    if len(password.encode("utf-8")) > _MAX_PASSWORD_BYTES:
        raise ValidationFailedError(f"Password must not exceed {_MAX_PASSWORD_BYTES} bytes.")
    if not _PASSWORD_POLICY_PATTERN.match(password):
        raise ValidationFailedError(
            "Password must be at least 8 characters and include an uppercase letter, "
            "a lowercase letter, a number, and a special character."
        )


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt. Only the hash is ever stored."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# ----------------------------------------------------------------------
# JWT Authentication (Security Architecture, Section 6; API Architecture, Section 11)
# ----------------------------------------------------------------------


class TokenType(str, Enum):
    """Distinguishes access from refresh tokens. Not itself a documented
    JWT claim value list, but required to tell the two apart when
    validating — access tokens authenticate requests; refresh tokens
    only mint new access tokens."""

    ACCESS = "access"
    REFRESH = "refresh"


def _create_token(*, user_id: uuid.UUID, email: str, role: UserRole, token_type: TokenType,
                   expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "role": role.value,
        "type": token_type.value,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(*, user_id: uuid.UUID, email: str, role: UserRole) -> str:
    """Creates a short-lived JWT access token containing the documented
    User ID, Email, Role, and Expiration Time claims."""
    return _create_token(
        user_id=user_id,
        email=email,
        role=role,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(*, user_id: uuid.UUID, email: str, role: UserRole) -> str:
    """Creates a longer-lived JWT refresh token, used only to mint new
    access tokens (Security Architecture Section 8 - Session Management)."""
    return _create_token(
        user_id=user_id,
        email=email,
        role=role,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str, *, expected_type: TokenType) -> dict[str, Any]:
    """
    Validates and decodes a JWT, raising `AuthenticationError` for any
    missing, malformed, expired, or wrong-type token so callers never
    need to handle raw `jwt` library exceptions.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid authentication token.") from exc

    if payload.get("type") != expected_type.value:
        raise AuthenticationError("Invalid token type for this operation.")
    return payload


__all__ = [
    "SecurityHeadersMiddleware",
    "validate_password_policy",
    "hash_password",
    "verify_password",
    "TokenType",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]