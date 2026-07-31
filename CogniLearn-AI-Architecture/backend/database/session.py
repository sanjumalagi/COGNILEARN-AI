"""
Database Session Management.

Configures the SQLAlchemy engine (with connection pooling) and provides
a request-scoped session factory used throughout the application.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.3 - Database Package)
Reference: 01_Project_Foundation/05_Technology_Stack.md (Section 4 - Database & ORM)
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT_SECONDS,
    pool_recycle=settings.DATABASE_POOL_RECYCLE_SECONDS,
    # Verifies a pooled connection is still alive before handing it out,
    # avoiding "server closed the connection unexpectedly" errors after
    # idle periods.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a request-scoped database session and
    guarantees it is closed afterwards, even if the request raises.

    Usage (from Module 2 onward):
        def endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
