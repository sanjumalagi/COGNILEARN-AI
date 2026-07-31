"""
Shared Dependencies.

Central location for FastAPI dependency-injection providers that are
reused across API routers.

Database session and current-user dependencies are intentionally left
undefined here — they will be introduced in Module 1 (Database Layer)
and Module 3 (Authentication) respectively, and re-exported from this
module once implemented so routers have a single, stable import path.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.2 - Core Package)
"""

from backend.config import Settings, get_settings

__all__ = ["get_settings", "Settings"]
