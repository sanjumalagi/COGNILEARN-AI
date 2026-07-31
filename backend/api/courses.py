"""
Course API.

Implements exactly the documented endpoints for the Course Module:
GET /courses, POST /courses, GET /courses/{id}, PUT /courses/{id},
DELETE /courses/{id}.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.3 - Course Module)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import Course, User
from backend.schemas.course import CourseCreate, CourseListResponse, CourseResponse, CourseUpdate
from backend.services.course_service import CourseService

router = APIRouter()


def _to_response(course: Course) -> CourseResponse:
    return CourseResponse(
        course_id=course.course_id,
        title=course.title,
        description=course.description,
        modules=len(course.modules),
    )


@router.get("/", response_model=CourseListResponse, summary="List courses")
def list_courses(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseListResponse:
    page = CourseService(db).list_courses(offset=offset, limit=limit)
    return CourseListResponse(
        items=[_to_response(c) for c in page.items], total=page.total, offset=page.offset, limit=page.limit
    )


@router.post(
    "/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED, summary="Create a course"
)
def create_course(
    payload: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseResponse:
    course = CourseService(db).create_course(actor=current_user, payload=payload)
    db.commit()
    return _to_response(course)


@router.get("/{course_id}", response_model=CourseResponse, summary="Get a course by ID")
def get_course(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseResponse:
    course = CourseService(db).get_course(course_id=course_id)
    return _to_response(course)


@router.put("/{course_id}", response_model=CourseResponse, summary="Replace a course")
def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseResponse:
    course = CourseService(db).update_course(actor=current_user, course_id=course_id, payload=payload)
    db.commit()
    return _to_response(course)


@router.delete(
    "/{course_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a course (Admin only)"
)
def delete_course(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    CourseService(db).delete_course(actor=current_user, course_id=course_id)
    db.commit()