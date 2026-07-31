"""
Schemas Package.

Pydantic request/response models (DTOs) used by the API layer for
validation and serialization, matching the documented API Data
Contracts.

Populated incrementally as each module (Auth, Users, Courses,
Assessments, Learner, Adaptive, AI, Analytics) is implemented.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md
"""

from backend.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    UserPublic,
)
from backend.schemas.user import (
    StudentProfileOut,
    StudentProfileUpdate,
    TeacherProfileOut,
    TeacherProfileUpdate,
    UserDetail,
    UserListResponse,
    UserUpdateRequest,
)

__all__ = [
    "RegisterRequest",
    "UserPublic",
    "LoginRequest",
    "LoginResponse",
    "RefreshRequest",
    "RefreshResponse",
    "LogoutResponse",
    "StudentProfileOut",
    "TeacherProfileOut",
    "UserDetail",
    "UserListResponse",
    "StudentProfileUpdate",
    "TeacherProfileUpdate",
    "UserUpdateRequest",
]