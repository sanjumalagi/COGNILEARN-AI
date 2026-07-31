"""
Shared Dependencies.

Central location for FastAPI dependency-injection providers that are
reused across API routers: settings, the database session, the
current-authenticated-user dependency, and Role-Based Access Control.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.2 - Core Package)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 9 - RBAC)
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.config import Settings, get_settings
from backend.core.exceptions import AuthenticationError, AuthorizationError
from backend.core.security import TokenType, decode_token
from backend.database import get_db
from backend.models import User, UserRole
from backend.repositories import UserRepository

# `auto_error=False` so a missing token raises our own AuthenticationError
# (with the documented error envelope) instead of FastAPI's default
# generic 403.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolves the authenticated User from the `Authorization: Bearer
    <token>` header.

    Raises `AuthenticationError` (401) for a missing, invalid, expired,
    or wrong-type token, or if the token's subject no longer exists.
    """
    if credentials is None:
        raise AuthenticationError("Missing authentication token.")

    payload = decode_token(credentials.credentials, expected_type=TokenType.ACCESS)

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid authentication token.") from exc

    user = UserRepository(db).find_by_id(user_id)
    if user is None:
        raise AuthenticationError("User no longer exists.")
    return user


def require_role(*allowed_roles: UserRole) -> Callable[[User], User]:
    """
    Dependency factory enforcing Role-Based Access Control.

    Usage (for future modules, per the documented Permission Matrix):
        @router.post("/courses", dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))])

    Raises `AuthorizationError` (403) if the authenticated user's role
    is not one of `allowed_roles`.
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError("You do not have permission to perform this action.")
        return current_user

    return dependency


__all__ = ["get_settings", "Settings", "get_db", "get_current_user", "require_role"]