"""
User & Profile Schemas.

Pydantic request/response models for the `/users` endpoints.

No dedicated profile sub-resource is documented (02_System_Architecture/
05_API_Architecture.md Section 23.2 lists only GET/GET/PATCH/DELETE on
`/api/v1/users`), so Student/Teacher profile fields are nested inside
the User request/response bodies rather than exposed as a separate route.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.2 - User Module)
Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Student/Teacher Profile)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from backend.models.enums import UserRole


class StudentProfileOut(BaseModel):
    """Read-only representation of a StudentProfile."""

    model_config = {"from_attributes": True}

    student_id: uuid.UUID
    enrollment_number: str
    program: str
    semester: int


class TeacherProfileOut(BaseModel):
    """Read-only representation of a TeacherProfile."""

    model_config = {"from_attributes": True}

    teacher_id: uuid.UUID
    department: str
    designation: str


class UserDetail(BaseModel):
    """Full representation of a User, including its role-appropriate profile."""

    model_config = {"from_attributes": True}

    user_id: uuid.UUID
    name: str
    email: str
    role: UserRole
    created_at: datetime
    student_profile: StudentProfileOut | None = None
    teacher_profile: TeacherProfileOut | None = None


class UserListResponse(BaseModel):
    """Paginated list of users, matching the shape already established by
    `backend.repositories.base.Page`."""

    items: list[UserDetail]
    total: int
    offset: int
    limit: int


class StudentProfileUpdate(BaseModel):
    """
    Partial update for a StudentProfile.

    All fields are required together the first time a profile is
    created (via PATCH /users/{id} on a user with no existing profile);
    any subset may be supplied when updating an existing profile.
    """

    enrollment_number: str | None = Field(default=None, min_length=1, max_length=255)
    program: str | None = Field(default=None, min_length=1, max_length=255)
    semester: int | None = Field(default=None, ge=1, le=20)


class TeacherProfileUpdate(BaseModel):
    """Partial update for a TeacherProfile (see StudentProfileUpdate docstring
    for creation-vs-update field requirements, which apply identically here)."""

    department: str | None = Field(default=None, min_length=1, max_length=255)
    designation: str | None = Field(default=None, min_length=1, max_length=255)


class UserUpdateRequest(BaseModel):
    """
    Request body for PATCH /users/{id}.

    All top-level fields are optional (partial update). `role` may only
    be changed by an Admin (enforced in UserService, not here, since it
    depends on who the acting user is).
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    role: UserRole | None = None
    student_profile: StudentProfileUpdate | None = None
    teacher_profile: TeacherProfileUpdate | None = None