"""
Module 1 — Database Layer Tests.

These tests run against a real, disposable PostgreSQL database (see
conftest.py) built from the ORM models, so foreign keys, cascade rules,
RESTRICT behavior, and unique constraints are verified against actual
database enforcement rather than mocks.
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import (
    AIInteraction,
    Assessment,
    AssessmentItem,
    AssessmentResponse,
    Course,
    LearnerProfile,
    LearningObjective,
    LearningPath,
    Module,
    ProgressHistory,
    Recommendation,
    StudentProfile,
    TeacherProfile,
    TeachingContext,
    Topic,
    TopicMastery,
    User,
    UserRole,
)


def _make_user(role: UserRole = UserRole.STUDENT, email: str | None = None) -> User:
    return User(
        name="Ada Lovelace",
        email=email or f"{uuid.uuid4()}@cognilearn.test",
        password_hash="hashed-password",
        role=role,
    )


def _make_course_topic(db_session: Session) -> Topic:
    course = Course(title="Intro to CS", description="Foundations of computer science")
    module = Module(course=course, title="Algorithms", sequence_number=1)
    topic = Topic(module=module, title="Sorting", description="Sorting algorithms", difficulty_level=2)
    db_session.add(course)
    db_session.flush()
    return topic


class TestFullHierarchy:
    """Verifies the complete documented entity graph can be created and read back."""

    def test_create_full_course_and_learner_hierarchy(self, db_session: Session) -> None:
        user = _make_user()
        student = StudentProfile(
            user=user, enrollment_number="ENR-001", program="Computer Science", semester=3
        )
        learner_profile = LearnerProfile(student=student, ability_theta=0.5, overall_mastery=0.4)
        db_session.add(user)
        db_session.flush()

        topic = _make_course_topic(db_session)
        objective = LearningObjective(topic=topic, description="Understand binary search")
        assessment = Assessment(topic=topic, title="Sorting Quiz", assessment_type="quiz")
        item = AssessmentItem(
            assessment=assessment,
            question_text="What is the complexity of binary search?",
            difficulty=0.6,
            bloom_level="Understand",
            correct_answer="O(log n)",
            explanation="Binary search halves the search space each step.",
        )
        db_session.add_all([objective, assessment, item])
        db_session.flush()

        response = AssessmentResponse(
            student=student,
            item=item,
            selected_answer="O(log n)",
            is_correct=True,
            response_time=12,
        )
        mastery = TopicMastery(learner_profile=learner_profile, topic=topic, mastery_score=0.75)
        recommendation = Recommendation(
            student=student, topic=topic, recommendation_type="revision", priority=1
        )
        path = LearningPath(student=student, topic=topic, sequence_order=1, status="pending")
        context = TeachingContext(
            student=student,
            topic=topic,
            teaching_strategy="Worked Example",
            learning_objective="Understand binary search",
            difficulty="Medium",
        )
        progress = ProgressHistory(student=student, topic=topic, mastery_score=0.75)
        db_session.add_all([response, mastery, recommendation, path, context, progress])
        db_session.flush()

        interaction = AIInteraction(
            context=context,
            ai_provider="gemini",
            prompt="Explain binary search",
            response="Binary search repeatedly halves the search interval...",
        )
        db_session.add(interaction)
        db_session.commit()

        # Read back through relationships, not raw IDs.
        fetched_user = db_session.get(User, user.user_id)
        assert fetched_user is not None
        assert fetched_user.student_profile.enrollment_number == "ENR-001"
        assert fetched_user.student_profile.learner_profile.ability_theta == pytest.approx(0.5)
        assert fetched_user.student_profile.learner_profile.topic_masteries[0].mastery_score == pytest.approx(
            0.75
        )
        assert fetched_user.student_profile.assessment_responses[0].is_correct is True
        assert fetched_user.student_profile.recommendations[0].recommendation_type == "revision"
        assert fetched_user.student_profile.teaching_contexts[0].ai_interactions[0].ai_provider == "gemini"

    def test_teacher_profile_roundtrip(self, db_session: Session) -> None:
        user = _make_user(role=UserRole.TEACHER)
        teacher = TeacherProfile(user=user, department="Computer Science", designation="Professor")
        db_session.add(user)
        db_session.commit()

        fetched = db_session.get(User, user.user_id)
        assert fetched.role == UserRole.TEACHER
        assert fetched.teacher_profile.designation == "Professor"
        assert teacher.teacher_id is not None


class TestConstraints:
    """Verifies constraints documented in Section 7 of the Database Schema."""

    def test_duplicate_email_is_rejected(self, db_session: Session) -> None:
        db_session.add(_make_user(email="duplicate@cognilearn.test"))
        db_session.commit()

        db_session.add(_make_user(email="duplicate@cognilearn.test"))
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_invalid_role_value_is_rejected_at_the_database_level(self, db_session: Session) -> None:
        # Bypasses the Python enum to prove the native Postgres ENUM
        # type itself rejects values outside Student/Teacher/Admin.
        with pytest.raises(Exception):  # noqa: B017 - asserting DB-level enum rejection
            db_session.execute(
                text(
                    "INSERT INTO users (user_id, name, email, password_hash, role, created_at) "
                    "VALUES (:id, 'X', 'x@example.com', 'hash', 'SuperAdmin', now())"
                ),
                {"id": str(uuid.uuid4())},
            )
            db_session.commit()


class TestCascadeDeletes:
    """Verifies the compositional-ownership cascade policy."""

    def test_deleting_course_cascades_to_modules_and_topics(self, db_session: Session) -> None:
        topic = _make_course_topic(db_session)
        course = topic.module.course
        db_session.commit()

        course_id, module_id, topic_id = course.course_id, topic.module.module_id, topic.topic_id

        db_session.delete(course)
        db_session.commit()

        assert db_session.get(Course, course_id) is None
        assert db_session.get(Module, module_id) is None
        assert db_session.get(Topic, topic_id) is None

    def test_deleting_user_cascades_to_student_and_learner_profile(self, db_session: Session) -> None:
        user = _make_user()
        student = StudentProfile(user=user, enrollment_number="ENR-002", program="CS", semester=1)
        learner_profile = LearnerProfile(student=student, ability_theta=0.0, overall_mastery=0.0)
        db_session.add(user)
        db_session.commit()

        user_id, student_id, lp_id = user.user_id, student.student_id, learner_profile.learner_profile_id

        db_session.delete(user)
        db_session.commit()

        assert db_session.get(User, user_id) is None
        assert db_session.get(StudentProfile, student_id) is None
        assert db_session.get(LearnerProfile, lp_id) is None


class TestRestrictDeletes:
    """Verifies the educational-record protection policy (Section 7: 'Restricted
    deletes for educational records')."""

    def test_topic_with_topic_mastery_cannot_be_deleted(self, db_session: Session) -> None:
        user = _make_user()
        student = StudentProfile(user=user, enrollment_number="ENR-003", program="CS", semester=2)
        learner_profile = LearnerProfile(student=student, ability_theta=0.2, overall_mastery=0.2)
        topic = _make_course_topic(db_session)
        db_session.add(user)
        db_session.add(TopicMastery(learner_profile=learner_profile, topic=topic, mastery_score=0.5))
        db_session.commit()

        db_session.delete(topic)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_student_with_assessment_response_cannot_be_deleted(self, db_session: Session) -> None:
        user = _make_user()
        student = StudentProfile(user=user, enrollment_number="ENR-004", program="CS", semester=2)
        topic = _make_course_topic(db_session)
        assessment = Assessment(topic=topic, title="Quiz", assessment_type="quiz")
        item = AssessmentItem(
            assessment=assessment,
            question_text="2 + 2?",
            difficulty=0.1,
            bloom_level="Remember",
            correct_answer="4",
            explanation="Basic arithmetic.",
        )
        db_session.add(user)
        db_session.add(item)
        db_session.flush()
        db_session.add(
            AssessmentResponse(
                student=student, item=item, selected_answer="4", is_correct=True, response_time=3
            )
        )
        db_session.commit()

        db_session.delete(student)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_assessment_item_with_response_cannot_be_deleted(self, db_session: Session) -> None:
        user = _make_user()
        student = StudentProfile(user=user, enrollment_number="ENR-005", program="CS", semester=2)
        topic = _make_course_topic(db_session)
        assessment = Assessment(topic=topic, title="Quiz", assessment_type="quiz")
        item = AssessmentItem(
            assessment=assessment,
            question_text="2 + 2?",
            difficulty=0.1,
            bloom_level="Remember",
            correct_answer="4",
            explanation="Basic arithmetic.",
        )
        db_session.add(user)
        db_session.add(item)
        db_session.flush()
        db_session.add(
            AssessmentResponse(
                student=student, item=item, selected_answer="4", is_correct=True, response_time=3
            )
        )
        db_session.commit()

        db_session.delete(item)
        with pytest.raises(IntegrityError):
            db_session.commit()
