"""
Configuration Package.

Stores application configuration: environment variables, database
settings, AI provider settings, and security configuration.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.9)
"""

from backend.config.settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
