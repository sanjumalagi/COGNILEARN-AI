"""
User Management API.

Implements exactly the documented endpoints for the User Module:
GET /users, GET /users/{id}, PATCH /users/{id}, DELETE /users/{id}.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.2 - User Module)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import User, UserRole
from backend.schemas.user import UserDetail, UserListResponse, UserUpdateRequest
from backend.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=UserListResponse, summary="List users (Admin only)")
def list_users(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    role: UserRole | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserListResponse:
    service = UserService(db)
    page = service.list_users(actor=current_user, offset=offset, limit=limit, role=role)
    return UserListResponse(items=page.items, total=page.total, offset=page.offset, limit=page.limit)


@router.get("/{user_id}", response_model=UserDetail, summary="Get a user by ID")
def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    service = UserService(db)
    return service.get_user(actor=current_user, target_id=user_id)


@router.patch("/{user_id}", response_model=UserDetail, summary="Update a user and/or their profile")
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    service = UserService(db)
    user = service.update_user(actor=current_user, target_id=user_id, payload=payload)
    db.commit()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user (Admin only)")
def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service = UserService(db)
    service.delete_user(actor=current_user, target_id=user_id)
    db.commit()