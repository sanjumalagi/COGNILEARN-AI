# API Reference
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | API Reference |
| Version | 1.0 |
| Status | Approved Appendix |
| Purpose | Provide comprehensive documentation of the REST APIs exposed by the CogniLearn AI platform for developers, administrators, and system integrators. |

---

# 1. Introduction

The CogniLearn AI platform exposes a RESTful API that enables communication between the frontend, backend services, Educational Intelligence modules, and external clients. All APIs exchange data using JSON over HTTPS and follow consistent naming, authentication, and error-handling conventions.

The API is versioned to support backward compatibility while allowing future enhancements.

---

# 2. API Overview

| Property | Value |
|----------|-------|
| Protocol | HTTPS |
| API Style | REST |
| Data Format | JSON |
| Authentication | JWT Bearer Token |
| Character Encoding | UTF-8 |
| Version | v1 |

Example Base URL:

```
https://api.cognilearn.ai/api/v1
```

---

# 3. API Architecture

```
Frontend (React)

        │

HTTPS REST API

        │

        ▼

FastAPI Backend

        │

        ▼

Business Services

        │

        ▼

Educational Intelligence

        │

        ▼

AI Service Layer

        │

        ▼

Gemini API
```

The frontend communicates only with the backend. Educational Intelligence and AI providers are not directly exposed.

---

# 4. Authentication

Authentication is performed using JSON Web Tokens (JWT).

Workflow:

```
User Login

      │

      ▼

JWT Generated

      │

      ▼

Client Stores Token

      │

      ▼

Authorization Header

      │

      ▼

Protected API Access
```

Authorization header:

```
Authorization: Bearer <JWT_TOKEN>
```

---

# 5. Authentication Endpoints

## Register

```
POST /auth/register
```

Request

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "StrongPassword123"
}
```

Response

```json
{
  "message": "User registered successfully"
}
```

---

## Login

```
POST /auth/login
```

Request

```json
{
  "email": "john@example.com",
  "password": "StrongPassword123"
}
```

Response

```json
{
  "access_token": "...",
  "token_type": "Bearer"
}
```

---

## Logout

```
POST /auth/logout
```

Response

```json
{
  "message":"Logout successful"
}
```

---

# 6. User APIs

## Get Profile

```
GET /users/profile
```

Response

```json
{
  "id":1,
  "full_name":"John Doe",
  "email":"john@example.com",
  "role":"student"
}
```

---

## Update Profile

```
PUT /users/profile
```

Request

```json
{
  "full_name":"John Doe"
}
```

---

# 7. Course APIs

## Get Courses

```
GET /courses
```

Returns all available courses.

---

## Get Course

```
GET /courses/{course_id}
```

Returns detailed course information.

---

## Create Course (Administrator)

```
POST /courses
```

---

## Update Course

```
PUT /courses/{course_id}
```

---

## Delete Course

```
DELETE /courses/{course_id}
```

---

# 8. Module APIs

```
GET /modules

GET /modules/{id}

POST /modules

PUT /modules/{id}

DELETE /modules/{id}
```

Modules belong to individual courses.

---

# 9. Topic APIs

```
GET /topics

GET /topics/{id}

POST /topics

PUT /topics/{id}

DELETE /topics/{id}
```

Topics organize learning concepts within modules.

---

# 10. Assessment APIs

## Start Assessment

```
POST /assessments/start
```

Request

```json
{
  "topic_id":12
}
```

---

## Generate Question

```
POST /assessments/question
```

Request

```json
{
    "assessment_id":25
}
```

---

## Submit Answer

```
POST /assessments/answer
```

Request

```json
{
    "assessment_id":25,
    "question_id":10,
    "selected_option":"B"
}
```

Response

```json
{
    "correct":true,
    "explanation":"..."
}
```

---

## Finish Assessment

```
POST /assessments/finish
```

Returns:

- Final score
- Theta estimate
- Topic mastery
- Recommendations

---

# 11. Educational Intelligence APIs

These endpoints interact with the Educational Intelligence layer.

## Learner Mastery

```
GET /learner/mastery
```

Returns:

- Topic mastery
- Knowledge estimates
- Learning progress

---

## Learning Path

```
GET /learner/path
```

Returns personalized learning recommendations.

---

## Recommendation

```
GET /learner/recommendation
```

Returns recommended next learning activities.

---

# 12. AI Tutor APIs

## Ask Tutor

```
POST /ai/tutor
```

Request

```json
{
  "question":"Explain Binary Search."
}
```

Response

```json
{
  "answer":"..."
}
```

The Educational Intelligence layer prepares the teaching context before the request reaches the AI Service Layer.

---

# 13. Analytics APIs

## Student Dashboard

```
GET /analytics/student
```

Returns

- Progress
- Assessment history
- Mastery
- Learning statistics

---

## Instructor Dashboard

```
GET /analytics/instructor
```

Returns aggregated learner statistics.

---

## Administrator Dashboard

```
GET /analytics/admin
```

Returns platform-wide operational statistics.

---

# 14. HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Resource Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Resource Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

# 15. Error Response Format

Example

```json
{
    "error":"ValidationError",
    "message":"Topic ID is required.",
    "status":422
}
```

Error responses follow a consistent JSON structure to simplify client-side handling.

---

# 16. API Versioning

The API uses URL-based versioning.

Example

```
/api/v1/
```

Future versions:

```
/api/v2/

/api/v3/
```

Versioning ensures backward compatibility while enabling new functionality.

---

# 17. Security Considerations

The API incorporates multiple security mechanisms:

- HTTPS communication
- JWT authentication
- Password hashing (bcrypt)
- RBAC authorization
- Input validation
- Prompt validation
- Response validation
- Rate limiting
- Secure CORS configuration
- Audit logging

Sensitive information is never returned in API responses.

---

# 18. Best Practices

Developers integrating with the API should:

- Always use HTTPS.
- Store JWT tokens securely.
- Handle API errors gracefully.
- Validate client-side input.
- Respect rate limits.
- Retry only transient failures.
- Keep API versions up to date.
- Avoid exposing sensitive credentials.

---

# 19. Relationship with Previous Documentation

| Document | Contribution |
|----------|--------------|
| Data & Model Design | API contracts and DTOs |
| Implementation Guide | Backend implementation |
| Deployment & Operations | API hosting and deployment |
| API Reference | Integration guide for developers |

This appendix provides practical usage details for the APIs defined throughout the project.

---

# 20. Summary

This document defined the REST API of CogniLearn AI, including authentication, user management, course management, adaptive assessments, Educational Intelligence services, AI Tutor interactions, analytics, error handling, versioning, and security.

The API follows RESTful principles, uses standardized JSON payloads, and ensures secure, maintainable, and scalable communication between system components.

---

# Guiding Principles

> APIs should be consistent, predictable, and versioned.

> Authentication and authorization should protect all sensitive resources.

> Educational Intelligence should remain internal and independent of external AI providers.

> AI-generated instructional content should only be accessed through the AI Service Layer.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**