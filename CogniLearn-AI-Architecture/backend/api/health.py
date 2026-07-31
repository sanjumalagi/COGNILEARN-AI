"""
Health Check Endpoint.

Provides a lightweight liveness/readiness endpoint used by Docker,
orchestration platforms, and monitoring tooling to verify that the
application process is up and correctly configured.

Reference: 02_System_Architecture/12_Observability_Architecture.md
Reference: 08_DEPLOYMENT_AND_OPERATIONS/05_MONITORING_AND_LOGGING.md
"""

from fastapi import APIRouter

from backend.config import settings

router = APIRouter()


@router.get("/health", summary="Application health check")
async def health_check() -> dict:
    """
    Returns basic application health and version information.

    This endpoint intentionally has no dependency on the database or
    external AI providers so it remains available even if those
    subsystems are degraded; deeper readiness checks (DB connectivity,
    AI provider reachability) will be added as those modules land.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
