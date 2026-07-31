"""
Authentication API.

Implements exactly the documented endpoints:
POST /auth/register, POST /auth/login, POST /auth/refresh,
POST /auth/logout, GET /auth/me.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 4 - Authentication APIs)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 11 - Authentication Architecture)
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.config import settings
from backend.core.dependencies import get_current_user
from backend.core.exceptions import AuthenticationError
from backend.core.security import TokenType, create_access_token, create_refresh_token, decode_token
from backend.database import get_db
from backend.models import User
from backend.repositories import UserRepository
from backend.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    UserPublic,
)
from backend.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    service = AuthService(db)
    user = service.register(
        name=payload.name, email=payload.email, password=payload.password, role=payload.role
    )
    db.commit()
    return user


@router.post("/login", response_model=LoginResponse, summary="Log in and receive JWT tokens")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    service = AuthService(db)
    user = service.authenticate(email=payload.email, password=payload.password)
    return LoginResponse(
        access_token=create_access_token(user_id=user.user_id, email=user.email, role=user.role),
        refresh_token=create_refresh_token(user_id=user.user_id, email=user.email, role=user.role),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Exchange a refresh token for a new access token",
)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> RefreshResponse:
    token_payload = decode_token(payload.refresh_token, expected_type=TokenType.REFRESH)

    user = UserRepository(db).find_by_id(uuid.UUID(token_payload["sub"]))
    if user is None:
        raise AuthenticationError("User no longer exists.")

    return RefreshResponse(
        access_token=create_access_token(user_id=user.user_id, email=user.email, role=user.role),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=LogoutResponse, summary="Log out (stateless)")
def logout(current_user: User = Depends(get_current_user)) -> LogoutResponse:
    # Server-side token revocation is documented as a future enhancement
    # (Security Architecture Section 8), so there is nothing to persist
    # here beyond confirming the caller was authenticated.
    return LogoutResponse()


@router.get("/me", response_model=UserPublic, summary="Get the current authenticated user")
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user