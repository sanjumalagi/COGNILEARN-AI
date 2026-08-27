"""
Database Test Fixtures.

Provides a session-scoped test database (created fresh from the ORM
models against a real PostgreSQL server) and a function-scoped SQLAlchemy
session, so Module 1 tests exercise actual foreign keys, cascade/restrict
behavior, and constraints rather than mocks.

Reference: 06_IMPLEMENTATION_GUIDE/00_IMPLEMENTATION_OVERVIEW.md
"""

from collections.abc import Generator

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings
from backend.models import Base

TEST_DB_NAME = "cognilearn_ai_test"


def _admin_engine() -> sa.Engine:
    """Engine connected to the `postgres` maintenance database, used only
    to create/drop the dedicated test database."""
    admin_url = sa.engine.make_url(settings.DATABASE_URL).set(database="postgres")
    return sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")


@pytest.fixture(scope="session")
def test_engine() -> Generator[sa.Engine, None, None]:
    """
    Creates a dedicated `cognilearn_ai_test` database, builds the full
    schema from the ORM models, yields an engine bound to it, then drops
    the database at the end of the test session.
    """
    admin_engine = _admin_engine()
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
        conn.execute(sa.text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    test_url = sa.engine.make_url(settings.DATABASE_URL).set(database=TEST_DB_NAME)
    engine = sa.create_engine(test_url)
    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()
    admin_engine = _admin_engine()
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
    admin_engine.dispose()


@pytest.fixture()
def db_session(test_engine: sa.Engine) -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session for a single test, truncating all tables
    afterward so each test starts from a clean, isolated state.
    """
    session_factory = sessionmaker(bind=test_engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        with test_engine.connect() as conn:
            table_names = ", ".join(f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables))
            conn.execute(sa.text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
            conn.commit()
