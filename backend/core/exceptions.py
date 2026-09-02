"""
Exception Handling Framework.

Defines the application's exception hierarchy and registers centralized
FastAPI exception handlers so every layer (API, services, educational
intelligence, AI service layer) raises typed, predictable errors instead
of leaking raw stack traces to clients.

Reference: 03_SOFTWARE_DESIGN/06_Error_handling_Design.md
Reference: 02_System_Architecture/02_Component_Architecture.md (Section 19)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 21 - Error Handling)
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.logging import get_logger

logger = get_logger(__name__)


class CogniLearnError(Exception):
    """
    Base class for every application-defined exception.

    All custom exceptions raised anywhere in the CogniLearn AI backend
    (services, repositories, algorithms, AI service layer) must inherit
    from this class so they can be handled consistently.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(CogniLearnError):
    """Raised when a requested entity does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"


class ValidationFailedError(CogniLearnError):
    """Raised when domain-level validation fails outside of Pydantic schemas."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_FAILED"


class AuthenticationError(CogniLearnError):
    """Raised when authentication fails (invalid credentials, expired token, etc.)."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_FAILED"


class AuthorizationError(CogniLearnError):
    """Raised when an authenticated user lacks permission for an action."""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_FAILED"


class ConflictError(CogniLearnError):
    """Raised when a request conflicts with the current state of a resource."""

    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"


class ExternalServiceError(CogniLearnError):
    """
    Raised when an external dependency fails.

    Used by the AI Service Layer when the LLM provider is unreachable,
    times out, or returns an invalid response.
    """

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "EXTERNAL_SERVICE_ERROR"


def _error_response(
    status_code: int, error_code: str, message: str, details: dict | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers all centralized exception handlers on the FastAPI application.

    Called once during application startup (see backend.main).
    """

    @app.exception_handler(CogniLearnError)
    async def handle_cognilearn_error(request: Request, exc: CogniLearnError) -> JSONResponse:
        logger.warning(
            "Handled application error: %s | path=%s | code=%s",
            exc.message,
            request.url.path,
            exc.error_code,
        )
        return _error_response(exc.status_code, exc.error_code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Pydantic v2 includes a `ctx` key in each error dict that can
        # hold the *raw exception instance* raised inside a
        # `field_validator` (e.g. `ValueError`) — not JSON-serializable.
        # Everything client-relevant is already in `msg`/`type`/`loc`, so
        # `ctx` is dropped rather than passed through to json.dumps().
        sanitized_errors = [
            {k: v for k, v in error.items() if k != "ctx"} for error in exc.errors()
        ]
        logger.info("Request validation failed | path=%s | errors=%s", request.url.path, sanitized_errors)
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "REQUEST_VALIDATION_FAILED",
            "The request could not be validated.",
            {"errors": sanitized_errors},
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on path=%s", request.url.path)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
        )