"""
Security Module (Skeleton).

Provides the security primitives that are shared application-wide:
security response headers and CORS wiring.

JWT issuance/verification, password hashing, and Role-Based Access
Control are documented as part of Module 3 (Authentication &
Authorization) and are intentionally NOT implemented here. This module
only establishes the security middleware skeleton required for a
runnable project baseline.

Reference: 02_System_Architecture/06_Security_Architecture.md
Reference: 01_Project_Foundation/05_Technology_Stack.md (Section 11)
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds standard, secure-by-default HTTP response headers to every
    response, per the "Secure by Default" principle in the Security
    Architecture document.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers.setdefault("X-Cognilearn-Version", "1.0.0")
        return response


__all__ = ["SecurityHeadersMiddleware"]
