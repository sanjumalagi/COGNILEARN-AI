"""
Module 2 — Repository Layer Tests.

Run against the same real, disposable PostgreSQL database used by the
Module 1 database tests (see conftest.py), so CRUD, pagination,
filtering, sorting, relationship loading, and transaction rollback are
verified against actual database behavior.
"""

import uuid

import pytest
from sqlalchemy.orm import Session

from backend.core.exceptions import ConflictError, NotFoundError
from backend.models import Course, Module, Topic, User, UserRole
from backend.repositories import (
    AssessmentRepository,
    CourseRepository,
    LearnerProfileRepository,
    ModuleRepository,
    StudentProfileRepository,
    TopicRepository,
    UserRepository,
)


def _unique_email() -> str:
    return f"{uuid.uuid4()}@cognilearn.test"


class TestBaseRepositoryCrud:
    """CRUD operations, exercised through UserRepository."""

    def test_create_find_update_delete(self, db_session: Session) -> None:
        repo = UserRepository(db_session)

        created = repo.create(
            name="Ada Lovelace",
            email=_unique_email(),
            password_hash="hash",
            role=UserRole.STUDENT,
        )
        db_session.commit()
        assert created.user_id is not None

        found = repo.find_by_id(created.user_id)
        assert found is not None
        assert found.name == "Ada Lovelace"

        updated = repo.update(created.user_id, name="Ada, Countess of Lovelace")
        db_session.commit()
        assert updated.name == "Ada, Countess of Lovelace"

        repo.delete(created.user_id)
        db_session.commit()
        assert repo.find_by_id(created.user_id) is None

    def test_save_persists_a_constructed_instance(self, db_session: Session) -> None:
        repo = UserRepository(db_session)
        user = User(name="Grace Hopper", email=_unique_email(), password_hash="hash", role=UserRole.TEACHER)

        saved = repo.save(user)
        db_session.commit()

        assert saved.user_id is not None
        assert repo.find_by_id(saved.user_id).name == "Grace Hopper"

    def test_update_missing_id_raises_not_found(self, db_session: Session) -> None:
        repo = UserRepository(db_session)
        with pytest.raises(NotFoundError):
            repo.update(uuid.uuid4(), name="Nobody")

    def test_delete_missing_id_raises_not_found(self, db_session: Session) -> None:
        repo = UserRepository(db_session)
        with pytest.raises(NotFoundError):
            repo.delete(uuid.uuid4())

    def test_duplicate_email_raises_conflict_and_rolls_back(self, db_session: Session) -> None:
        repo = UserRepository(db_session)
        email = _unique_email()
        repo.create(name="First", email=email, password_hash="hash", role=UserRole.STUDENT)
        db_session.commit()

        with pytest.raises(ConflictError):
            repo.create(name="Second", email=email, password_hash="hash", role=UserRole.STUDENT)

        # The failed create should not have left a half-committed row.
        page = repo.find_all(email=email)
        assert page.total == 1


class TestPaginationFilteringSorting:
    def test_find_all_paginates_filters_and_sorts(self, db_session: Session) -> None:
        repo = CourseRepository(db_session)
        for i in range(5):
            repo.create(title=f"Course {i}", description="A course.")
        db_session.commit()

        page_1 = repo.find_all(offset=0, limit=2, order_by=Course.title)
        page_2 = repo.find_all(offset=2, limit=2, order_by=Course.title)

        assert page_1.total == 5
        assert len(page_1.items) == 2
        assert [c.title for c in page_1.items] == ["Course 0", "Course 1"]
        assert [c.title for c in page_2.items] == ["Course 2", "Course 3"]

    def test_find_all_equality_filter(self, db_session: Session) -> None:
        repo = UserRepository(db_session)
        target_email = _unique_email()
        repo.create(name="Findme", email=target_email, password_hash="hash", role=UserRole.STUDENT)
        repo.create(name="Other", email=_unique_email(), password_hash="hash", role=UserRole.STUDENT)
        db_session.commit()

        page = repo.find_all(email=target_email)
        assert page.total == 1
        assert page.items[0].name == "Findme"

    def test_find_all_descending_sort(self, db_session: Session) -> None:
        repo = CourseRepository(db_session)
        repo.create(title="A", description="d")
        repo.create(title="B", description="d")
        db_session.commit()

        page = repo.find_all(order_by=Course.title, descending=True, limit=10)
        titles = [c.title for c in page.items]
        assert titles.index("B") < titles.index("A")

    def test_count(self, db_session: Session) -> None:
        repo = CourseRepository(db_session)
        repo.create(title="X", description="d")
        repo.create(title="Y", description="d")
        db_session.commit()

        assert repo.count() == 2
        assert repo.count(title="X") == 1

    def test_invalid_filter_field_raises_value_error(self, db_session: Session) -> None:
        repo = CourseRepository(db_session)
        with pytest.raises(ValueError):
            repo.find_all(not_a_real_field="x")


class TestRelationshipLoading:
    def test_user_repository_eager_loads_student_profile(self, db_session: Session) -> None:
        user_repo = UserRepository(db_session)
        student_repo = StudentProfileRepository(db_session)

        user = user_repo.create(
            name="Learner", email=_unique_email(), password_hash="hash", role=UserRole.STUDENT
        )
        db_session.flush()
        student_repo.create(user_id=user.user_id, enrollment_number="E-1", program="CS", semester=1)
        db_session.commit()
        db_session.expunge_all()

        fetched = user_repo.find_by_id(user.user_id)
        assert fetched.student_profile is not None
        assert fetched.student_profile.enrollment_number == "E-1"

    def test_course_repository_eager_loads_modules(self, db_session: Session) -> None:
        course_repo = CourseRepository(db_session)
        module_repo = ModuleRepository(db_session)

        course = course_repo.create(title="CS101", description="Intro")
        db_session.flush()
        module_repo.create(course_id=course.course_id, title="Basics", sequence_number=1)
        db_session.commit()
        db_session.expunge_all()

        fetched = course_repo.find_by_id(course.course_id)
        assert len(fetched.modules) == 1
        assert fetched.modules[0].title == "Basics"


class TestDocumentedCustomMethods:
    """The two documented methods beyond generic CRUD: findByTopic, findByModule."""

    def _make_topic(self, db_session: Session) -> Topic:
        course = Course(title="C", description="d")
        module = Module(course=course, title="M", sequence_number=1)
        topic = Topic(module=module, title="T", description="d", difficulty_level=1)
        db_session.add(course)
        db_session.flush()
        return topic

    def test_assessment_repository_find_by_topic(self, db_session: Session) -> None:
        topic = self._make_topic(db_session)
        repo = AssessmentRepository(db_session)
        repo.create(topic_id=topic.topic_id, title="Quiz 1", assessment_type="quiz")
        repo.create(topic_id=topic.topic_id, title="Quiz 2", assessment_type="quiz")
        db_session.commit()

        page = repo.find_by_topic(topic.topic_id)
        assert page.total == 2
        assert {a.title for a in page.items} == {"Quiz 1", "Quiz 2"}

    def test_topic_repository_find_by_module(self, db_session: Session) -> None:
        topic = self._make_topic(db_session)
        db_session.commit()
        repo = TopicRepository(db_session)

        page = repo.find_by_module(topic.module_id)
        assert page.total == 1
        assert page.items[0].topic_id == topic.topic_id


class TestTransactionRollback:
    def test_rollback_discards_uncommitted_changes(self, db_session: Session) -> None:
        repo = UserRepository(db_session)
        user = repo.create(
            name="Temporary", email=_unique_email(), password_hash="hash", role=UserRole.STUDENT
        )
        user_id = user.user_id

        db_session.rollback()

        assert repo.find_by_id(user_id) is None

    def test_rollback_after_commit_does_not_undo_committed_row(self, db_session: Session) -> None:
        repo = UserRepository(db_session)
        user = repo.create(
            name="Permanent", email=_unique_email(), password_hash="hash", role=UserRole.STUDENT
        )
        db_session.commit()
        user_id = user.user_id

        repo.update(user_id, name="Changed but uncommitted")
        db_session.rollback()

        fetched = repo.find_by_id(user_id)
        assert fetched.name == "Permanent"


class TestLearnerProfileRepository:
    """ILearnerRepository: save, findById, update, delete."""

    def test_full_crud_cycle(self, db_session: Session) -> None:
        user_repo = UserRepository(db_session)
        student_repo = StudentProfileRepository(db_session)
        learner_repo = LearnerProfileRepository(db_session)

        user = user_repo.create(
            name="L", email=_unique_email(), password_hash="hash", role=UserRole.STUDENT
        )
        db_session.flush()
        student = student_repo.create(
            user_id=user.user_id, enrollment_number="E-2", program="CS", semester=2
        )
        db_session.flush()

        created = learner_repo.create(
            student_id=student.student_id, ability_theta=0.0, overall_mastery=0.0
        )
        db_session.commit()

        updated = learner_repo.update(created.learner_profile_id, ability_theta=1.2)
        db_session.commit()
        assert updated.ability_theta == pytest.approx(1.2)

        learner_repo.delete(created.learner_profile_id)
        db_session.commit()
        assert learner_repo.find_by_id(created.learner_profile_id) is None