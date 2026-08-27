"""
Database Package.

Manages database connectivity, SQLAlchemy session lifecycle, and ORM
base class configuration.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.3)
"""

from backend.database.base import Base, TimestampMixin
from backend.database.session import SessionLocal, engine, get_db

__all__ = ["Base", "TimestampMixin", "SessionLocal", "engine", "get_db"]
