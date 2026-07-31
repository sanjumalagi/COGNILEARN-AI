"""
Module API.

Implements the documented Module API operations: Create, Update,
Delete, Get, List — at `/api/v1/modules`.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.4 - Module API)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas.module import ModuleCreate, ModuleListResponse, ModuleResponse, ModuleUpdate
from backend.services.module_service import ModuleService

router = APIRouter()


@router.get("/", response_model=ModuleListResponse, summary="List modules")
def list_modules(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    course_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ModuleListResponse:
    page = ModuleService(db).list_modules(offset=offset, limit=limit, course_id=course_id)
    return ModuleListResponse(items=page.items, total=page.total, offset=page.offset, limit=page.limit)


@router.post(
    "/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED, summary="Create a module"
)
def create_module(
    payload: ModuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ModuleResponse:
    module = ModuleService(db).create_module(actor=current_user, payload=payload)
    db.commit()
    return module


@router.get("/{module_id}", response_model=ModuleResponse, summary="Get a module by ID")
def get_module(
    module_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ModuleResponse:
    return ModuleService(db).get_module(module_id=module_id)


@router.put("/{module_id}", response_model=ModuleResponse, summary="Replace a module")
def update_module(
    module_id: uuid.UUID,
    payload: ModuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ModuleResponse:
    module = ModuleService(db).update_module(actor=current_user, module_id=module_id, payload=payload)
    db.commit()
    return module


@router.delete(
    "/{module_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a module (Admin only)"
)
def delete_module(
    module_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    ModuleService(db).delete_module(actor=current_user, module_id=module_id)
    db.commit()