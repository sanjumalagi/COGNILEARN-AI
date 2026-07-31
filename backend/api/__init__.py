"""
API Package.

Provides REST API endpoints for communication between the frontend and
backend. Each business capability (auth, courses, assessments, learner,
adaptive, ai, analytics) will register its own router here as its
module is implemented.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.1)
Reference: 02_System_Architecture/05_API_Architecture.md
"""

from fastapi import APIRouter

from backend.api.auth import router as auth_router
from backend.api.assessment_items import router as assessment_items_router
from backend.api.assessments import router as assessments_router
from backend.api.courses import router as courses_router
from backend.api.health import router as health_router
from backend.api.learner import router as learner_router
from backend.api.learning_objectives import router as learning_objectives_router
from backend.api.modules import router as modules_router
from backend.api.topics import router as topics_router
from backend.api.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])
api_router.include_router(modules_router, prefix="/modules", tags=["Modules"])
api_router.include_router(topics_router, prefix="/topics", tags=["Topics"])
api_router.include_router(
    learning_objectives_router, prefix="/learning-outcomes", tags=["Learning Outcomes"]
)
api_router.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(
    assessment_items_router, prefix="/assessment-items", tags=["Assessment Items"]
)
api_router.include_router(learner_router, prefix="/learner", tags=["Learner"])

# Future routers, registered as each module is implemented:
# api_router.include_router(adaptive_router, prefix="/adaptive", tags=["Adaptive Learning"])
# api_router.include_router(ai_router, prefix="/ai", tags=["AI Tutor"])
# api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])

__all__ = ["api_router"]