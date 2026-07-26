# CogniLearn AI

## An Intelligent AI Learning Companion

This is the application implementation of CogniLearn AI, built to faithfully
match the architecture, design, and algorithm documentation in
[`sanjumalagi/COGNILEARN-AI`](https://github.com/sanjumalagi/COGNILEARN-AI).
That documentation repository is the single source of truth for this
codebase — see it for full architectural context.

## Architecture

```
Assessment Intelligence → Learning Intelligence → Adaptive Intelligence → Teaching Intelligence
                                                                                 │
                                                                                 ▼
                                                                          AI Service Layer
                                                                                 │
                                                                                 ▼
                                                                       Large Language Model
```

Educational Intelligence makes every educational decision. The LLM only
generates instructional content.

## Current Status

**Module 0 — Project Bootstrap** ✅

A fully runnable project skeleton with no business logic yet:

- FastAPI backend with configuration, logging, centralized exception
  handling, security-header middleware, CORS, and a `/health` endpoint
- React + TypeScript + Tailwind frontend, wired to call the backend
- Docker + Docker Compose for backend, frontend, and PostgreSQL
- Automated bootstrap tests (backend)

Subsequent modules (Database Layer, Repository Layer, Authentication,
Course Management, Assessment/Learning/Adaptive/Teaching Intelligence, AI
Service Layer, Analytics, Frontend features, Testing, Deployment) are
implemented incrementally — see the Implementation Guide in the docs repo
for the full module order.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| AI Provider | Google Gemini (via an abstracted AI Service Layer) |
| Auth | JWT, RBAC |
| Deployment | Docker, Docker Compose |

## Getting Started

### Option A — Docker Compose (recommended)

```bash
cp backend/.env.example backend/.env
# fill in backend/.env (at minimum SECRET_KEY, GEMINI_API_KEY once AI is wired up)

docker compose up --build
```

- Backend: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/api/v1/docs
- Frontend: http://localhost:5173

### Option B — Run locally

**Backend**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env   # set DATABASE_URL to a local Postgres or sqlite:///./dev.db for now

# Run from the project root (not from inside backend/) so the
# `backend` package is importable:
uvicorn backend.main:app --reload
```

**Backend tests**

```bash
cd backend
pytest
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Project Structure

```
backend/
├── api/            # REST endpoints
├── core/           # logging, exceptions, security middleware, shared DI
├── database/       # SQLAlchemy session/base (Module 1)
├── models/         # ORM entities (Module 1)
├── repositories/   # persistence layer (Module 2)
├── services/       # business logic per capability
├── algorithms/     # IRT, BKT, adaptive engine
├── schemas/        # Pydantic DTOs
├── config/         # environment-driven settings
└── tests/

frontend/
├── src/
│   ├── components/  ├── pages/     ├── services/
│   ├── hooks/       ├── context/   ├── layouts/
│   ├── routes/      ├── types/     └── utils/

docker/
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.frontend.conf
```

## Documentation

Full architectural, algorithmic, and API documentation lives in the
[COGNILEARN-AI documentation repository](https://github.com/sanjumalagi/COGNILEARN-AI).
This implementation repository does not duplicate it — implementation
decisions defer to that documentation wherever the two might diverge.
