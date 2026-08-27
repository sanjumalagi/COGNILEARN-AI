"""
Database Enumerations.

Defines Python enums backing SQLAlchemy Enum columns.

Only `User.role` is explicitly typed as `ENUM(Student, Teacher, Admin)`
in the documented schema; every other VARCHAR-typed field (bloom_level,
assessment_type, recommendation_type, learning path status, teaching
strategy, difficulty, ai_provider) is left as a plain string column to
avoid imposing a value set the documentation does not define.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - User)
"""

import enum


class UserRole(str, enum.Enum):
    """The three documented user roles."""

    STUDENT = "Student"
    TEACHER = "Teacher"
    ADMIN = "Admin"
