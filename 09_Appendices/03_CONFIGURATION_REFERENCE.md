# Configuration Reference
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Configuration Reference |
| Version | 1.0 |
| Status | Approved Appendix |
| Purpose | Document all configurable parameters, environment variables, deployment settings, security configurations, AI provider settings, and operational configurations for the CogniLearn AI platform. |

---

# 1. Introduction

The Configuration Reference provides a centralized guide for configuring the CogniLearn AI platform. It describes application settings, environment variables, database parameters, authentication settings, AI provider configuration, logging, deployment profiles, and infrastructure settings.

Externalizing configuration enables the platform to support multiple deployment environments without modifying application source code.

---

# 2. Configuration Philosophy

CogniLearn AI follows these configuration principles:

- Environment-specific configuration.
- Secure secret management.
- Minimal hardcoded values.
- Externalized application settings.
- Provider-independent AI configuration.
- Infrastructure portability.
- Production-ready defaults.
- Version-controlled non-sensitive configuration.

---

# 3. Configuration Hierarchy

```
Application Configuration

        │

        ▼

Environment Variables (.env)

        │

        ▼

Application Settings

        │

        ▼

Database Configuration

        │

        ▼

AI Provider Configuration

        │

        ▼

Infrastructure Configuration
```

Configuration values are loaded in a layered manner, allowing environment-specific overrides.

---

# 4. Environment Variables

All sensitive configuration should be stored in a `.env` file.

Example:

```env
APP_NAME=CogniLearn AI
APP_ENV=development
APP_VERSION=1.0.0

SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The `.env` file should never be committed to version control.

---

# 5. Application Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| APP_NAME | Application name | CogniLearn AI |
| APP_ENV | Runtime environment | development |
| APP_VERSION | Software version | 1.0.0 |
| DEBUG | Debug mode | True / False |
| API_PREFIX | REST API prefix | /api/v1 |

---

# 6. Database Configuration

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cognilearn
DB_USER=postgres
DB_PASSWORD=strong_password
DATABASE_URL=postgresql://postgres:password@localhost:5432/cognilearn
```

Database settings include:

- Host
- Port
- Database name
- Username
- Password
- Connection URL

---

# 7. Authentication Configuration

JWT configuration:

```env
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

These values control authentication and session management.

---

# 8. AI Provider Configuration

The AI Service Layer is provider-independent.

Primary provider:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.5-pro
```

Future providers:

```env
OPENAI_API_KEY=
CLAUDE_API_KEY=
LLAMA_ENDPOINT=
MISTRAL_API_KEY=
DEEPSEEK_API_KEY=
```

Only one provider needs to be active at a time.

---

# 9. Educational Intelligence Configuration

Representative configurable parameters:

| Parameter | Purpose |
|-----------|---------|
| DEFAULT_THETA | Initial learner ability estimate |
| MIN_MASTERY | Lower mastery threshold |
| TARGET_MASTERY | Desired mastery level |
| QUESTION_BATCH_SIZE | Questions generated per assessment cycle |
| MAX_RECOMMENDATIONS | Maximum personalized recommendations |

Educational algorithms should expose configurable thresholds without requiring source code modification.

---

# 10. Frontend Configuration

Example:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=CogniLearn AI
VITE_ENABLE_ANALYTICS=true
```

Frontend configuration includes:

- Backend API URL
- Application branding
- Feature flags
- Analytics settings

---

# 11. Backend Configuration

Representative backend settings:

```env
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=INFO
```

These parameters determine runtime behavior of the FastAPI application.

---

# 12. Logging Configuration

Example:

```env
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/application.log
LOG_ROTATION=daily
```

Logging configuration controls:

- Log level.
- Output format.
- Log file location.
- Rotation policy.
- Retention period.

---

# 13. Docker Configuration

Representative Docker settings:

```yaml
version: "3.9"

services:
  backend:
    build: ./backend

  frontend:
    build: ./frontend

  database:
    image: postgres:16
```

Container configuration should remain environment independent wherever possible.

---

# 14. Nginx Configuration

Typical settings include:

- HTTPS termination.
- Reverse proxy rules.
- Static file serving.
- Request routing.
- Compression.
- Security headers.

Representative configuration:

```nginx
server {
    listen 443 ssl;

    location / {
        proxy_pass http://backend;
    }
}
```

---

# 15. Security Configuration

Representative settings:

```env
ENABLE_CORS=true
RATE_LIMIT=100
ALLOWED_ORIGINS=http://localhost:5173
PASSWORD_MIN_LENGTH=8
```

Security configuration includes:

- CORS.
- Rate limiting.
- Password policy.
- HTTPS enforcement.
- Allowed origins.

---

# 16. Deployment Profiles

Representative environments:

| Environment | Purpose |
|-------------|---------|
| Development | Local software development |
| Testing | Automated testing |
| Staging | Pre-production validation |
| Production | Live deployment |

Each environment should use independent configuration values.

---

# 17. Configuration Validation

During application startup, configuration should be validated.

Validation includes:

- Required variables present.
- Secret keys configured.
- Database connectivity.
- AI provider availability.
- Port availability.
- File permissions.
- Directory existence.

Startup should fail if critical configuration is invalid.

---

# 18. Configuration Management Best Practices

Recommended practices:

- Never hardcode secrets.
- Store credentials securely.
- Use different secrets per environment.
- Rotate sensitive keys periodically.
- Document configuration changes.
- Validate configuration during startup.
- Encrypt backups containing secrets.

---

# 19. Relationship with Previous Documentation

| Document | Contribution |
|----------|--------------|
| Infrastructure Setup | Server configuration |
| Cloud Deployment | Cloud environment |
| CI/CD Pipeline | Deployment automation |
| Deployment & Operations | Runtime configuration |
| Configuration Reference | Complete configuration handbook |

This appendix provides the operational details required to configure the platform consistently across all supported environments.

---

# 20. Summary

This document described the configuration framework for CogniLearn AI, including environment variables, application settings, database configuration, authentication, Educational Intelligence parameters, AI provider settings, frontend and backend configuration, logging, Docker, Nginx, deployment profiles, and configuration validation.

By externalizing configuration, the platform remains portable, secure, maintainable, and adaptable to a variety of deployment environments.

---

# Guiding Principles

> Configuration should be externalized rather than hardcoded.

> Sensitive values should always be securely managed.

> Different environments should maintain independent configurations.

> Educational Intelligence parameters should be configurable without modifying application logic.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**