"""
Application Settings.

Centralized, environment-driven configuration for CogniLearn AI.

This module is the single source of truth for runtime configuration.
All other packages (core, database, services, ai, etc.) must read
configuration through the `settings` object exported here rather than
reading environment variables directly.

Reference: 01_Project_Foundation/05_Technology_Stack.md
Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.9 - Configuration Package)
"""

from functools import lru_cache
from typing import List

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Strongly typed application settings loaded from environment variables
    or a `.env` file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = "CogniLearn AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    DEBUG: bool = Field(default=True)
    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    # Stored as a raw comma-separated string so pydantic-settings does not
    # attempt to JSON-decode it as a complex type; exposed as a list via
    # the computed `BACKEND_CORS_ORIGINS` property below.
    CORS_ORIGINS_RAW: str = Field(default="http://localhost:5173")

    @computed_field  # type: ignore[misc]
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    # ------------------------------------------------------------------
    # Database (wired in Module 1)
    # ------------------------------------------------------------------
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://cognilearn:cognilearn@localhost:5432/cognilearn_ai"
    )
    DATABASE_ECHO: bool = Field(default=False)
    DATABASE_POOL_SIZE: int = Field(default=5)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)
    DATABASE_POOL_TIMEOUT_SECONDS: int = Field(default=30)
    DATABASE_POOL_RECYCLE_SECONDS: int = Field(default=1800)

    # ------------------------------------------------------------------
    # Security (wired in Module 3)
    # ------------------------------------------------------------------
    SECRET_KEY: str = Field(default="CHANGE_ME_IN_PRODUCTION_this_default_is_not_secure_replace_it")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    @field_validator("SECRET_KEY")
    @classmethod
    def _check_secret_key_length(cls, value: str) -> str:
        # RFC 7518 Section 3.2 recommends an HMAC key of at least the
        # hash size in bytes (32 for HS256); PyJWT warns below that.
        if len(value.encode("utf-8")) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 bytes long (RFC 7518 Section 3.2 minimum for HS256)."
            )
        return value

    # ------------------------------------------------------------------
    # Learning Intelligence: IRT (wired in Module 7)
    # ------------------------------------------------------------------
    # 04_ALGORITHM_DESIGN/01_ITEM_RESPONSE_THEORY_DESIGN.md specifies the
    # 1PL (Rasch) model P(theta) = 1 / (1 + e^-(theta - b)) and says to
    # "estimate ability (theta)", but does not specify the numerical
    # estimation procedure. These settings configure the standard
    # Newton-Raphson MLE solver for that exact documented model.
    IRT_MAX_ITERATIONS: int = Field(default=50)
    IRT_CONVERGENCE_THRESHOLD: float = Field(default=1e-4)
    # Clamps applied only to keep all-correct/all-incorrect response
    # patterns (where unconstrained MLE diverges to +/-infinity) finite
    # and deterministic, per Section 14's "Produce deterministic results".
    IRT_ABILITY_MIN: float = Field(default=-4.0)
    IRT_ABILITY_MAX: float = Field(default=4.0)

    # ------------------------------------------------------------------
    # Learning Intelligence: BKT (wired in Module 7)
    # ------------------------------------------------------------------
    # 04_ALGORITHM_DESIGN/02_BAYESIAN_KNOWLEDGE_TRACING_DESIGN.md Section 7
    # names the four standard BKT parameters (P(L0), P(T), P(G), P(S)) but
    # does not supply numeric values. These are the widely-cited baseline
    # defaults from the original Corbett & Anderson BKT literature.
    BKT_PRIOR_L0: float = Field(default=0.3, ge=0.0, le=1.0)
    BKT_PROB_TRANSITION: float = Field(default=0.3, ge=0.0, le=1.0)
    BKT_PROB_GUESS: float = Field(default=0.2, ge=0.0, le=1.0)
    BKT_PROB_SLIP: float = Field(default=0.1, ge=0.0, le=1.0)

    # ------------------------------------------------------------------
    # AI Service Layer (implementation deferred to Module 9)
    # ------------------------------------------------------------------
    AI_PROVIDER: str = Field(default="gemini")
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro")
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 3

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = Field(default="INFO")
    LOG_JSON: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Using lru_cache ensures the .env file is parsed only once per process
    while still allowing settings to be overridden in tests via
    dependency overrides.
    """
    return Settings()


settings = get_settings()