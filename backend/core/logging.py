"""
Logging Infrastructure.

Provides a single, consistent logging configuration for the entire
backend application. All modules should obtain loggers through
`get_logger(__name__)` rather than configuring logging themselves.

Reference: 02_System_Architecture/12_Observability_Architecture.md
Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.2 - Core Package)
"""

import logging
import sys
from logging.config import dictConfig

from backend.config import settings


class JsonLogFormatter(logging.Formatter):
    """
    Minimal JSON log formatter used when structured logging is enabled.

    Structured logs are easier to ingest into log aggregation and
    monitoring systems in production deployments.
    """

    def format(self, record: logging.LogRecord) -> str:
        import json

        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> None:
    """
    Configures the root logging setup for the application.

    Called once during application startup (see backend.main).
    """
    formatter_key = "json" if settings.LOG_JSON else "standard"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JsonLogFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": formatter_key,
                "stream": sys.stdout,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
        },
        "loggers": {
            "uvicorn": {"handlers": ["console"], "level": settings.LOG_LEVEL, "propagate": False},
            "uvicorn.error": {"handlers": ["console"], "level": settings.LOG_LEVEL, "propagate": False},
            "uvicorn.access": {"handlers": ["console"], "level": settings.LOG_LEVEL, "propagate": False},
        },
    }

    dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a module-scoped logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("Assessment submitted", extra={"student_id": student_id})
    """
    return logging.getLogger(name)
