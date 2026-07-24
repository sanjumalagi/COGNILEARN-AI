# API Architecture
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | API Architecture |
| Version | 1.0 |
| Status | Approved Architecture Document |
| Purpose | Define the API architecture, communication standards, endpoint organization, request/response formats, authentication strategy, and integration workflow for CogniLearn AI. |

---

# 1. Introduction

The API Architecture defines how different components of CogniLearn AI communicate using RESTful APIs.

The API layer acts as the communication interface between:

- Frontend Application
- Backend Services
- Educational Intelligence Layer
- AI Service Layer
- Database

The API architecture is designed to be:

- Modular
- Secure
- Scalable
- Versioned
- Easy to maintain
- Easy to extend

---

# 2. API Design Philosophy

The API architecture follows five guiding principles.

---

## Service-Oriented

Every endpoint represents a business capability rather than a database table.

Examples:

✔ Generate Assessment

✔ Submit Assessment

✔ Get Learning Progress

✔ Generate Explanation

Instead of:

✖ Insert Question

✖ Update Topic

---

## Resource-Based

Resources are represented using nouns.

Examples

```
/courses

/modules

/topics

/assessments

/learning-outcomes

/users
```

Actions are represented using HTTP methods.

---

## Stateless

Every request contains all information required to process it.

The server does not maintain session state between requests.

Authentication is performed using JWT tokens.

---

## Layered

Requests move through well-defined architectural layers.

```
Frontend

↓

API Layer

↓

Business Services

↓

Educational Intelligence

↓

AI Service Layer

↓

Repository Layer

↓

Database
```

---

## Consistent

All APIs follow the same conventions for:

- URLs
- Authentication
- Validation
- Error handling
- Responses
- Status codes

---

# 3. API Architecture Overview

```
                React Frontend

                       │

                 HTTPS / REST

                       │

                       ▼

               FastAPI Controllers

                       │

             Request Validation

                       │

                       ▼

               Business Services

      ┌────────────┬──────────────┐

      ▼            ▼              ▼

Assessment    Learner      AI Service

      │            │              │

      └──────┬─────┴───────┬──────┘

             ▼             ▼

      Repository Layer

             │

             ▼

        PostgreSQL
```

---

# 4. API Layers

The API architecture consists of six logical layers.

---

## Layer 1 — Presentation Layer

Receives HTTP requests.

Responsibilities:

- Routing
- Authentication
- Validation
- Serialization

Technologies:

- FastAPI
- Pydantic

---

## Layer 2 — Service Layer

Contains business logic.

Examples:

- Course Service
- Assessment Service
- Learner Service
- Analytics Service
- AI Service

---

## Layer 3 — Educational Intelligence Layer

Responsible for:

- IRT
- BKT
- Adaptive Intelligence

This layer performs educational reasoning before AI is invoked.

---

## Layer 4 — AI Service Layer

Responsible for:

- Prompt Builder
- Context Manager
- Provider Adapter
- Response Parser

---

## Layer 5 — Repository Layer

Handles database communication.

Uses SQLAlchemy ORM.

Responsibilities:

- CRUD
- Queries
- Transactions

---

## Layer 6 — Database

Stores persistent data.

Uses PostgreSQL.

---

# 5. API Modules

The backend is organized into functional API modules.

```
/auth

/users

/courses

/modules

/topics

/learning-outcomes

/resources

/assessment-blueprints

/assessment-items

/assessments

/learner

/adaptive

/analytics

/ai
```

Each module represents a bounded context.

---

# 6. REST Standards

The API follows REST architectural principles.

---

## GET

Retrieve resources.

Examples

```
GET /courses

GET /courses/{id}

GET /learner/profile
```

---

## POST

Create new resources.

Examples

```
POST /courses

POST /assessments

POST /ai/explain
```

---

## PUT

Replace an existing resource.

Example

```
PUT /courses/{id}
```

---

## PATCH

Partially update a resource.

Example

```
PATCH /learner/profile
```

---

## DELETE

Remove a resource.

Example

```
DELETE /courses/{id}
```

---

# 7. URL Design

URLs follow a consistent naming convention.

Good examples

```
/courses

/modules

/topics

/assessment-items

/learning-outcomes

/learner/profile

/analytics/dashboard
```

Avoid:

```
/getCourse

/createTopic

/updateModule

/deleteQuestion
```

Resources should always be represented as nouns.

---

# 8. API Versioning

Versioning ensures backward compatibility.

Pattern:

```
/api/v1/
```

Examples:

```
/api/v1/courses

/api/v1/assessments

/api/v1/analytics

/api/v1/ai
```

Future versions:

```
/api/v2/

...

/api/v3/
```

---

# 9. Request Lifecycle

Every API request follows the same processing pipeline.

```
Client Request

        │

        ▼

Authentication

        │

        ▼

Validation

        │

        ▼

Business Service

        │

        ▼

Educational Intelligence

        │

        ▼

AI Service (Optional)

        │

        ▼

Repository

        │

        ▼

Database

        │

        ▼

Response
```

---

# 10. API Principles

The API architecture follows these principles:

- Stateless communication
- Separation of concerns
- Resource-oriented endpoints
- Consistent naming
- Strong validation
- Secure authentication
- Predictable responses
- Version compatibility

These principles ensure that the API remains maintainable, scalable, and suitable for long-term evolution.

---

# End of Part 1

# 11. Authentication Architecture

Authentication verifies the identity of users before granting access to protected resources.

CogniLearn AI uses **JWT (JSON Web Token)** based authentication to provide a stateless and scalable authentication mechanism.

---

## Authentication Flow

```
User Login

      │

      ▼

Authentication API

      │

      ▼

Verify Credentials

      │

      ▼

Generate JWT Token

      │

      ▼

Return Access Token

      │

      ▼

Client Stores Token

      │

      ▼

Token Sent in Authorization Header
```

---

## Authorization Header

Every protected request includes:

```
Authorization: Bearer <JWT_TOKEN>
```

---

## JWT Payload

Example payload:

```json
{
  "sub": "user_id",
  "email": "student@example.com",
  "role": "Student",
  "exp": 1719999999
}
```

---

## Authentication Responsibilities

The Authentication Service is responsible for:

- User registration
- Login
- Password verification
- Password hashing
- JWT generation
- JWT validation
- Token expiration handling

---

# 12. Role-Based Access Control (RBAC)

Authorization is implemented using Role-Based Access Control.

---

## Supported Roles

| Role | Responsibilities |
|------|-------------------|
| Student | Learn, attempt assessments, interact with AI tutor |
| Teacher | Manage courses, resources, assessments |
| Administrator | Full system management |

---

## Permission Matrix

| Resource | Student | Teacher | Admin |
|-----------|----------|----------|--------|
| View Courses | ✓ | ✓ | ✓ |
| Create Course | ✗ | ✓ | ✓ |
| Edit Course | ✗ | ✓ | ✓ |
| Delete Course | ✗ | ✗ | ✓ |
| Attempt Assessment | ✓ | ✗ | ✗ |
| Upload Resources | ✗ | ✓ | ✓ |
| Generate AI Explanation | ✓ | ✓ | ✓ |
| View Analytics | Own | Course | All |

---

# 13. Request Standards

Every API request follows a standardized format.

---

## Headers

Required headers:

```
Authorization: Bearer <token>

Content-Type: application/json

Accept: application/json
```

---

## Request Body

Example:

```json
{
  "course_id": "uuid",
  "title": "Introduction to Machine Learning",
  "description": "Course overview"
}
```

---

## Path Parameters

Example:

```
GET /courses/{course_id}
```

---

## Query Parameters

Example:

```
GET /courses?page=1&limit=20
```

---

# 14. Response Standards

Every successful response follows a consistent structure.

---

## Success Response

```json
{
  "success": true,
  "message": "Course created successfully.",
  "data": {
    ...
  }
}
```

---

## List Response

```json
{
  "success": true,
  "total": 25,
  "page": 1,
  "page_size": 10,
  "data": [
    ...
  ]
}
```

---

## Error Response

```json
{
  "success": false,
  "error": {
    "code": "COURSE_NOT_FOUND",
    "message": "The requested course does not exist."
  }
}
```

---

# 15. Pydantic DTO Architecture

The API uses Pydantic Data Transfer Objects (DTOs) for validation and serialization.

Each module should define separate DTOs for:

- Create Request
- Update Request
- Response
- Summary
- Detailed View

Example:

```
course/

├── course_create.py
├── course_update.py
├── course_response.py
├── course_summary.py
└── course_detail.py
```

Separating DTOs improves maintainability and prevents overexposing internal data.

---

# 16. HTTP Status Codes

The API uses standard HTTP status codes.

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

# 17. Validation Strategy

Input validation occurs before business logic execution.

Validation includes:

- Required fields
- Data types
- String lengths
- Email format
- UUID format
- Date format
- Enum values
- Numeric ranges

Business-specific validation is handled within the service layer.

Examples:

- Course title uniqueness
- Learning Outcome code uniqueness
- Assessment publication rules

---

# 18. Exception Handling

Exceptions are centrally managed using FastAPI exception handlers.

---

## Common Exceptions

- Validation Error
- Authentication Error
- Authorization Error
- Resource Not Found
- Database Error
- AI Service Error
- External API Error

---

## Error Flow

```
Exception

      │

      ▼

Global Exception Handler

      │

      ▼

Standardized Error Response

      │

      ▼

Frontend
```

---

# 19. API Security

The API incorporates multiple security mechanisms.

---

## Authentication

JWT-based authentication.

---

## Authorization

Role-Based Access Control.

---

## Password Security

Passwords are stored using bcrypt hashing.

---

## Input Validation

All user inputs are validated before processing.

---

## SQL Injection Prevention

Database access is performed exclusively through SQLAlchemy ORM and parameterized queries.

---

## CORS

Only trusted frontend origins should be permitted.

---

## Environment Variables

Sensitive configuration values such as API keys and database credentials are stored in environment variables.

---

# 20. Rate Limiting

Rate limiting protects the API from abuse.

Recommended limits:

| Endpoint | Suggested Limit |
|----------|-----------------|
| Login | 5 requests/minute |
| Registration | 3 requests/minute |
| AI Requests | 30 requests/minute |
| Assessment Submission | 10 requests/minute |
| General API | 100 requests/minute |

Rate limiting should be configurable based on deployment requirements.

---

# 21. Pagination

Large collections should be paginated.

Example request:

```
GET /courses?page=2&limit=20
```

Example response:

```json
{
  "page": 2,
  "page_size": 20,
  "total_pages": 8,
  "total_records": 154,
  "data": [...]
}
```

---

# 22. Filtering and Sorting

APIs should support filtering and sorting where appropriate.

Example:

```
GET /courses?published=true&sort=title&order=asc
```

Supported operations may include:

- Filtering
- Sorting
- Searching
- Pagination

This reduces unnecessary data transfer and improves frontend performance.

---

# Part 2 Summary

This section established the standards for:

- JWT Authentication
- Role-Based Access Control
- Request and Response formats
- DTO design
- HTTP status codes
- Validation
- Exception handling
- API security
- Rate limiting
- Pagination
- Filtering and sorting

These standards ensure consistency across all API endpoints and provide a secure, predictable interface for frontend and third-party integrations.

---

# End of Part 2

# 23. API Endpoint Architecture

The API is organized into domain-specific modules. Each module represents a business capability rather than a database entity.

---

## 23.1 Authentication Module

**Base Path**

```
/api/v1/auth
```

### Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /register | Register new user |
| POST | /login | Authenticate user |
| POST | /refresh | Refresh access token |
| POST | /logout | Logout user |
| GET | /me | Retrieve authenticated user profile |

---

## 23.2 User Module

**Base Path**

```
/api/v1/users
```

### Endpoints

| Method | Endpoint |
|---------|----------|
| GET | / |
| GET | /{id} |
| PATCH | /{id} |
| DELETE | /{id} |

---

## 23.3 Course Module

**Base Path**

```
/api/v1/courses
```

### Endpoints

| Method | Endpoint |
|---------|----------|
| GET | / |
| POST | / |
| GET | /{id} |
| PUT | /{id} |
| DELETE | /{id} |

---

## 23.4 Module API

```
/api/v1/modules
```

Operations:

- Create Module
- Update Module
- Delete Module
- Get Module
- List Modules

---

## 23.5 Topic API

```
/api/v1/topics
```

Operations:

- Create Topic
- Update Topic
- Delete Topic
- List Topics

---

## 23.6 Learning Outcome API

```
/api/v1/learning-outcomes
```

Operations:

- Create Learning Outcome
- Update Learning Outcome
- View Learning Outcome
- List Learning Outcomes

---

## 23.7 Learning Resource API

```
/api/v1/resources
```

Operations:

- Upload Resource
- Update Resource
- Delete Resource
- Download Resource
- List Resources

---

## 23.8 Assessment Module

```
/api/v1/assessments
```

Endpoints:

| Method | Endpoint |
|---------|----------|
| POST | /generate |
| POST | /submit |
| GET | /{id} |
| GET | /history |
| GET | /results |

---

## 23.9 Learner Module

```
/api/v1/learner
```

Endpoints:

| Method | Endpoint |
|---------|----------|
| GET | /profile |
| GET | /mastery |
| GET | /ability |
| GET | /progress |
| GET | /history |

---

## 23.10 Adaptive Learning Module

```
/api/v1/adaptive
```

Endpoints:

| Method | Endpoint |
|---------|----------|
| GET | /recommendations |
| GET | /learning-path |
| GET | /next-learning-outcome |
| GET | /revision-plan |

---

## 23.11 AI Module

```
/api/v1/ai
```

Endpoints:

| Method | Endpoint |
|---------|----------|
| POST | /explain |
| POST | /hint |
| POST | /feedback |
| POST | /summary |
| POST | /chat |

---

## 23.12 Analytics Module

```
/api/v1/analytics
```

Endpoints:

| Method | Endpoint |
|---------|----------|
| GET | /dashboard |
| GET | /performance |
| GET | /progress |
| GET | /mastery |
| GET | /reports |

---

# 24. API Interaction Workflows

---

## Assessment Workflow

```
Student

      │

      ▼

Assessment API

      │

      ▼

Assessment Service

      │

      ▼

Educational Intelligence

      │

      ▼

Database

      │

      ▼

Response
```

---

## AI Explanation Workflow

```
Student

      │

      ▼

AI API

      │

      ▼

AI Service

      │

      ▼

Prompt Builder

      │

      ▼

Context Manager

      │

      ▼

LLM Provider

      │

      ▼

Response Parser

      │

      ▼

Student
```

---

## Adaptive Recommendation Workflow

```
Student

      │

      ▼

Adaptive API

      │

      ▼

Adaptive Engine

      │

      ▼

IRT

      │

      ▼

BKT

      │

      ▼

Recommendation

      │

      ▼

Frontend
```

---

# 25. API Sequence Diagram

Example: AI Explanation Request

```
Student

      │

      ▼

Frontend

      │

      ▼

POST /ai/explain

      │

      ▼

FastAPI Controller

      │

      ▼

AI Service

      │

      ▼

Prompt Builder

      │

      ▼

Gemini API

      │

      ▼

Response Parser

      │

      ▼

Frontend

      │

      ▼

Student
```

---

# 26. OpenAPI Integration

FastAPI automatically generates OpenAPI documentation.

Benefits include:

- Interactive API documentation
- Automatic request validation
- Automatic response schemas
- Client SDK generation
- Easy testing

Documentation endpoints:

```
/docs

/redoc

/openapi.json
```

---

# 27. API Testing Strategy

The API should be tested at multiple levels.

---

## Unit Testing

Tests:

- Individual services
- Utility functions
- Validation logic

---

## Integration Testing

Tests:

- API endpoints
- Database interactions
- Authentication flow
- AI integration

---

## End-to-End Testing

Tests complete user workflows.

Examples:

- User registration
- Course creation
- Assessment attempt
- AI explanation
- Adaptive recommendation

---

## Performance Testing

Evaluate:

- Response time
- Throughput
- Concurrent users
- Database performance
- AI request latency

---

# 28. API Documentation Standards

Every endpoint should include:

- Summary
- Description
- Request schema
- Response schema
- Error responses
- Authentication requirements
- Example requests
- Example responses

Example:

```
POST /api/v1/ai/explain

Summary:
Generate a personalized explanation for a Learning Outcome.

Authentication:
Required

Request Body:
ExplainRequest

Response:
ExplanationResponse
```

---

# 29. API Versioning Strategy

Current version:

```
v1
```

Future versions:

```
v2

v3
```

Versioning principles:

- Never introduce breaking changes within the same version.
- Deprecate endpoints before removal.
- Provide migration guidance for major releases.
- Maintain backward compatibility whenever practical.

---

# 30. API Architectural Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| AD-01 | Use REST architecture | Widely adopted, simple integration |
| AD-02 | Use FastAPI | High performance with automatic OpenAPI support |
| AD-03 | JWT authentication | Stateless and scalable authentication |
| AD-04 | Separate controllers from services | Improves maintainability |
| AD-05 | Repository pattern for persistence | Decouples business logic from database |
| AD-06 | Centralized exception handling | Consistent error responses |
| AD-07 | Standardized response format | Predictable frontend integration |
| AD-08 | Version APIs | Enables long-term evolution |

---

# 31. API Quality Attributes

The API architecture is designed to satisfy the following quality attributes:

- Scalability
- Reliability
- Security
- Maintainability
- Testability
- Extensibility
- Consistency
- Performance

---

# 32. API Architecture Summary

The API Architecture provides a secure, modular, and scalable communication layer for CogniLearn AI.

It connects the frontend, Educational Intelligence Layer, AI Service Layer, and database through well-defined RESTful interfaces.

The architecture emphasizes:

- Resource-oriented endpoint design
- Stateless communication
- JWT-based authentication
- Role-based authorization
- Consistent validation
- Standardized request and response models
- Comprehensive documentation
- Version compatibility

By separating routing, business logic, educational intelligence, AI services, and persistence, the API remains maintainable and adaptable as the platform evolves.

---

# API Guiding Principles

> Every endpoint represents a business capability.

> Business logic belongs in the service layer, not controllers.

> Educational reasoning occurs before AI interaction.

> APIs should be predictable, secure, and versioned.

> Responses should be standardized and self-descriptive.

> Authentication and authorization are mandatory for protected resources.

> APIs should remain implementation-independent and consumer-friendly.

---

**End of Document**