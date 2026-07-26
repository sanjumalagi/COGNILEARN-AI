"""
CogniLearn AI — Backend Application Entrypoint.

Bootstraps the FastAPI application: configuration, logging, exception
handling, security middleware, CORS, and API routing.

Business logic (database models, authentication, educational
intelligence, AI service layer, etc.) is intentionally NOT wired in
yet — those are implemented in subsequent modules and registered here
incrementally as they land.

Run locally:
    uvicorn backend.main:app --reload

Reference: 02_System_Architecture/01_High_Level_Architecture.md
Reference: 06_IMPLEMENTATION_GUIDE/00_IMPLEMENTATION_OVERVIEW.md
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import api_router
from backend.config import settings
from backend.core.exceptions import register_exception_handlers
from backend.core.logging import configure_logging, get_logger
from backend.core.security import SecurityHeadersMiddleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan handler.

    Startup and shutdown hooks currently only log process lifecycle
    events; database connection pooling and AI client initialization
    will be added here as those modules are implemented.
    """
    logger.info(
        "%s v%s starting in %s mode",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("%s shutting down", settings.APP_NAME)


def create_app() -> FastAPI:
    """
    Application factory.

    Using a factory (rather than a module-level singleton built via side
    effects) keeps the app importable and re-creatable in tests without
    global state leaking between test cases.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="An Intelligent AI Learning Companion — adaptive assessment "
        "and learning platform combining Assessment, Learning, Adaptive, "
        "and Teaching Intelligence.",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(SecurityHeadersMiddleware)

    register_exception_handlers(application)

    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
