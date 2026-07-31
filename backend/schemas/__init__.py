"""
Schemas Package.

Pydantic request/response models (DTOs) used by the API layer for
validation and serialization, matching the documented API Data
Contracts.

Populated incrementally as each module (Auth, Users, Courses,
Assessments, Learner, Adaptive, AI, Analytics) is implemented.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md
"""

from backend.schemas.assessment import (
    AssessmentCreate,
    AssessmentDetail,
    AssessmentListResponse,
    AssessmentUpdate,
)
from backend.schemas.assessment_attempt import (
    AssessmentHistoryItem,
    AssessmentHistoryResponse,
    AssessmentResultResponse,
    GenerateAssessmentRequest,
    GeneratedAssessmentResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from backend.schemas.assessment_item import (
    AssessmentItemCreate,
    AssessmentItemDetail,
    AssessmentItemListResponse,
    AssessmentItemPublic,
    AssessmentItemUpdate,
)
from backend.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    UserPublic,
)
from backend.schemas.course import CourseCreate, CourseListResponse, CourseResponse, CourseUpdate
from backend.schemas.learning_objective import (
    LearningObjectiveCreate,
    LearningObjectiveListResponse,
    LearningObjectiveResponse,
    LearningObjectiveUpdate,
)
from backend.schemas.module import ModuleCreate, ModuleListResponse, ModuleResponse, ModuleUpdate
from backend.schemas.topic import TopicCreate, TopicListResponse, TopicResponse, TopicUpdate
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
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseListResponse",
    "ModuleCreate",
    "ModuleUpdate",
    "ModuleResponse",
    "ModuleListResponse",
    "TopicCreate",
    "TopicUpdate",
    "TopicResponse",
    "TopicListResponse",
    "LearningObjectiveCreate",
    "LearningObjectiveUpdate",
    "LearningObjectiveResponse",
    "LearningObjectiveListResponse",
    "AssessmentCreate",
    "AssessmentUpdate",
    "AssessmentDetail",
    "AssessmentListResponse",
    "AssessmentItemCreate",
    "AssessmentItemUpdate",
    "AssessmentItemDetail",
    "AssessmentItemListResponse",
    "AssessmentItemPublic",
    "GenerateAssessmentRequest",
    "GeneratedAssessmentResponse",
    "SubmitAnswerRequest",
    "SubmitAnswerResponse",
    "AssessmentResultResponse",
    "AssessmentHistoryItem",
    "AssessmentHistoryResponse",
]