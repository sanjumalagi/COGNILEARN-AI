"""
Shared Dependencies.

Central location for FastAPI dependency-injection providers that are
reused across API routers.

The current-user dependency is intentionally left undefined here — it
will be introduced in Module 3 (Authentication) and re-exported from
this module once implemented so routers have a single, stable import
path.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.2 - Core Package)
"""

from backend.config import Settings, get_settings
from backend.database import get_db

__all__ = ["get_settings", "Settings", "get_db"]
