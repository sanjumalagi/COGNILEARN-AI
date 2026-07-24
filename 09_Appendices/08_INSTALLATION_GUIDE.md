# Installation Guide
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Installation Guide |
| Version | 1.0 |
| Status | Approved Appendix |
| Purpose | Provide comprehensive instructions for installing, configuring, deploying, and verifying the CogniLearn AI platform in development, testing, and production environments. |

---

# 1. Introduction

This Installation Guide describes the complete process for setting up the CogniLearn AI platform.

The guide includes:

- System requirements
- Software prerequisites
- Project setup
- Backend installation
- Frontend installation
- Database configuration
- Environment configuration
- Docker deployment
- Production deployment
- Verification procedures

Following this guide ensures a consistent and reliable installation across different environments.

---

# 2. System Requirements

## Minimum Hardware

| Component | Minimum Requirement |
|-----------|---------------------|
| CPU | Dual Core Processor |
| Memory | 8 GB RAM |
| Storage | 20 GB Free Disk Space |
| Network | Stable Internet Connection |

---

## Recommended Hardware

| Component | Recommended |
|-----------|-------------|
| CPU | Quad-Core Processor or Higher |
| Memory | 16 GB RAM |
| Storage | SSD with 50 GB Free Space |
| Network | High-Speed Broadband |

---

# 3. Supported Operating Systems

CogniLearn AI supports:

- Ubuntu Linux 22.04 LTS or later
- Windows 11
- macOS Ventura or later

Linux is recommended for production deployments.

---

# 4. Software Prerequisites

Install the following software before beginning the installation.

| Software | Recommended Version |
|----------|---------------------|
| Python | 3.12+ |
| Node.js | 20 LTS |
| npm | Latest Stable |
| PostgreSQL | 16+ |
| Git | Latest Stable |
| Docker | Latest Stable |
| Docker Compose | Latest Stable |

---

# 5. Clone the Repository

Clone the project repository.

```bash
git clone https://github.com/your-organization/cognilearn-ai.git

cd cognilearn-ai
```

---

# 6. Project Structure

```
CogniLearn-AI/

backend/

frontend/

documentation/

tests/

docker/

.env.example
```

Verify that all required directories are present before continuing.

---

# 7. Backend Installation

Navigate to the backend directory.

```bash
cd backend
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the environment.

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# 8. Frontend Installation

Navigate to the frontend directory.

```bash
cd frontend
```

Install project dependencies.

```bash
npm install
```

Start the development server.

```bash
npm run dev
```

---

# 9. Database Setup

Create a PostgreSQL database.

Example:

```sql
CREATE DATABASE cognilearn;
```

Apply database migrations.

```bash
alembic upgrade head
```

Verify that all required tables have been created successfully.

---

# 10. Environment Configuration

Create a `.env` file in the backend directory.

Example:

```env
APP_ENV=development
APP_NAME=CogniLearn AI

DATABASE_URL=postgresql://postgres:password@localhost:5432/cognilearn

JWT_SECRET_KEY=replace_with_secure_key
JWT_ALGORITHM=HS256

AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.5-pro
```

Sensitive configuration values should never be committed to version control.

---

# 11. Running the Backend

Start the FastAPI application.

```bash
uvicorn main:app --reload
```

The backend API should now be available.

Example:

```
http://localhost:8000
```

---

# 12. Running the Frontend

Start the frontend.

```bash
npm run dev
```

Example:

```
http://localhost:5173
```

The frontend should connect to the backend using the configured API endpoint.

---

# 13. Running the Complete System

Start the following services:

- PostgreSQL
- Backend
- Frontend

System workflow:

```
Browser

     │

     ▼

Frontend

     │

     ▼

FastAPI

     │

     ▼

Educational Intelligence

     │

     ▼

AI Service Layer

     │

     ▼

Gemini API

     │

     ▼

PostgreSQL
```

---

# 14. Docker Installation

Build containers.

```bash
docker compose build
```

Start all services.

```bash
docker compose up -d
```

Verify running containers.

```bash
docker ps
```

---

# 15. Production Deployment

Recommended production components:

- Ubuntu Server
- Nginx
- Gunicorn/Uvicorn
- PostgreSQL
- Docker
- SSL Certificates
- Reverse Proxy
- Firewall

Deployment should follow the procedures described in the Deployment and Operations documentation.

---

# 16. Post-Installation Verification

Verify the following:

| Verification | Expected Result |
|--------------|----------------|
| Backend API | Running |
| Frontend | Accessible |
| Database | Connected |
| Authentication | Operational |
| Adaptive Assessment | Functional |
| AI Tutor | Responding |
| Analytics | Available |

Perform basic functional tests before releasing the platform for use.

---

# 17. Initial Administrator Setup

After installation:

1. Create the first administrator account.
2. Verify administrator login.
3. Configure AI provider credentials.
4. Create initial courses.
5. Create modules and topics.
6. Verify learner registration.
7. Perform a sample adaptive assessment.

These steps prepare the platform for operational use.

---

# 18. Common Installation Issues

| Issue | Possible Cause | Resolution |
|--------|----------------|------------|
| Database connection failed | Incorrect database credentials | Verify `.env` configuration |
| Backend fails to start | Missing dependencies | Install required packages |
| Frontend cannot connect | Incorrect API URL | Check frontend configuration |
| Authentication errors | Invalid JWT secret | Verify authentication settings |
| AI Tutor unavailable | Missing API key | Configure AI provider credentials |
| Migration failure | Database version mismatch | Review migration history |

---

# 19. Updating the Platform

To update the platform:

1. Pull the latest source code.
2. Install updated dependencies.
3. Apply database migrations.
4. Restart backend services.
5. Restart frontend services.
6. Verify application functionality.

Updates should be tested in a staging environment before production deployment.

---

# 20. Relationship with Previous Documentation

| Document | Contribution |
|----------|--------------|
| Configuration Reference | Environment settings |
| Deployment & Operations | Infrastructure deployment |
| Developer Guide | Development workflow |
| Installation Guide | Installation procedures |

This guide translates deployment planning into practical installation steps.

---

# 21. Summary

This Installation Guide described the complete installation process for CogniLearn AI, including prerequisite software, backend and frontend setup, database configuration, environment variables, Docker deployment, production recommendations, verification procedures, administrator initialization, troubleshooting, and platform updates.

Following this guide ensures a secure, reliable, and repeatable installation process suitable for both development and production environments.

---

# Guiding Principles

> Installation should be repeatable across supported environments.

> Configuration should remain externalized and secure.

> Production deployments should prioritize reliability, security, and maintainability.

> Educational Intelligence should operate independently of the underlying AI provider.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**