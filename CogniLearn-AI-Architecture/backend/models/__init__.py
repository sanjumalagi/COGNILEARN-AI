"""
Models Package.

Defines all SQLAlchemy ORM entities documented in
05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md.

Every model must be imported here so that `Base.metadata` (used by
Alembic autogenerate and `Base.metadata.create_all()`) is aware of the
complete schema, and so relationship string references (e.g.
`Mapped["Topic"]`) resolve correctly at mapper-configuration time.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md
"""

from backend.database.base import Base
from backend.models.ai_interaction import AIInteraction
from backend.models.assessment import Assessment
from backend.models.assessment_item import AssessmentItem
from backend.models.assessment_response import AssessmentResponse
from backend.models.course import Course
from backend.models.enums import UserRole
from backend.models.learner_profile import LearnerProfile
from backend.models.learning_objective import LearningObjective
from backend.models.learning_path import LearningPath
from backend.models.module import Module
from backend.models.progress_history import ProgressHistory
from backend.models.recommendation import Recommendation
from backend.models.student_profile import StudentProfile
from backend.models.teacher_profile import TeacherProfile
from backend.models.teaching_context import TeachingContext
from backend.models.topic import Topic
from backend.models.topic_mastery import TopicMastery
from backend.models.user import User

__all__ = [
    "Base",
    "UserRole",
    "User",
    "StudentProfile",
    "TeacherProfile",
    "Course",
    "Module",
    "Topic",
    "LearningObjective",
    "Assessment",
    "AssessmentItem",
    "AssessmentResponse",
    "LearnerProfile",
    "TopicMastery",
    "Recommendation",
    "LearningPath",
    "TeachingContext",
    "AIInteraction",
    "ProgressHistory",
]
