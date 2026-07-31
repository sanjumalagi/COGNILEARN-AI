"""
Repository Package.

Provides database access abstraction (CRUD, query execution,
persistence) that isolates business logic from ORM/database details.

Implementation is delivered in Module 2 - Repository Layer.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5)
"""
"""
Repository Package.

Provides database access abstraction (CRUD, pagination, filtering,
sorting) that isolates business logic from ORM/database details, per
the documented Repository Interfaces.

`AnalyticsRepository` (documented in 03_Interface_Design.md Section 6)
is intentionally NOT implemented here: its operations
(learnerAnalytics, assessmentAnalytics, topicAnalytics) are aggregation
queries tied to the Analytics module, not CRUD persistence for one of
the 17 entities this layer covers. It belongs with Module 11
(Analytics), not Module 2 (Repository Layer).

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5)
Reference: 03_SOFTWARE_DESIGN/03_Interface_Design.md (Section 6 - Repository Interfaces)
"""

from backend.repositories.ai_interaction_repository import AIInteractionRepository
from backend.repositories.assessment_item_repository import AssessmentItemRepository
from backend.repositories.assessment_repository import AssessmentRepository
from backend.repositories.assessment_response_repository import AssessmentResponseRepository
from backend.repositories.base import BaseRepository, Page
from backend.repositories.course_repository import CourseRepository
from backend.repositories.learner_profile_repository import LearnerProfileRepository
from backend.repositories.learning_objective_repository import LearningObjectiveRepository
from backend.repositories.learning_path_repository import LearningPathRepository
from backend.repositories.module_repository import ModuleRepository
from backend.repositories.progress_history_repository import ProgressHistoryRepository
from backend.repositories.recommendation_repository import RecommendationRepository
from backend.repositories.student_profile_repository import StudentProfileRepository
from backend.repositories.teacher_profile_repository import TeacherProfileRepository
from backend.repositories.teaching_context_repository import TeachingContextRepository
from backend.repositories.topic_mastery_repository import TopicMasteryRepository
from backend.repositories.topic_repository import TopicRepository
from backend.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "Page",
    "UserRepository",
    "StudentProfileRepository",
    "TeacherProfileRepository",
    "CourseRepository",
    "ModuleRepository",
    "TopicRepository",
    "LearningObjectiveRepository",
    "AssessmentRepository",
    "AssessmentItemRepository",
    "AssessmentResponseRepository",
    "LearnerProfileRepository",
    "TopicMasteryRepository",
    "RecommendationRepository",
    "LearningPathRepository",
    "TeachingContextRepository",
    "AIInteractionRepository",
    "ProgressHistoryRepository",
]