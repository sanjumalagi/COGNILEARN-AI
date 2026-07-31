# API Data Contracts
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | API Data Contracts |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the standardized request and response data models exchanged between the frontend, backend, Educational Intelligence layer, and AI Service Layer within CogniLearn AI. |

---

# 1. Introduction

The API Data Contracts define the communication interface between the frontend and backend services of CogniLearn AI.

A data contract specifies the structure of every request and response exchanged through the REST API. Standardized contracts ensure consistency, maintainability, interoperability, and reliable integration across all system components.

Rather than exposing internal database models directly, the API uses dedicated Data Transfer Objects (DTOs) that represent only the information required by clients.

---

# 2. Objectives

The API Data Contracts aim to:

- Standardize API communication.
- Decouple frontend from database implementation.
- Support versioned APIs.
- Improve maintainability.
- Simplify validation.
- Enable independent frontend and backend development.
- Ensure consistent error handling.

---

# 3. API Design Principles

The API follows these principles:

- RESTful architecture
- JSON-based communication
- Stateless requests
- Versioned endpoints
- Consistent naming conventions
- Standard HTTP status codes
- DTO-based communication
- Secure authentication using JWT

---

# 4. Authentication APIs

## Login Request

```json
{
  "email": "student@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "access_token": "jwt_token",
  "token_type": "Bearer",
  "expires_in": 3600,
  "role": "Student"
}
```

---

## Register Request

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "Student"
}
```

---

# 5. Course APIs

## Course Response

```json
{
  "course_id": "CSE101",
  "title": "Data Structures",
  "description": "Introduction to Data Structures",
  "modules": 6
}
```

---

## Module Response

```json
{
  "module_id": "M01",
  "course_id": "CSE101",
  "title": "Arrays"
}
```

---

## Topic Response

```json
{
  "topic_id": "T101",
  "module_id": "M01",
  "title": "Binary Search",
  "difficulty": "Medium"
}
```

---

# 6. Assessment APIs

## Start Assessment Request

```json
{
  "student_id": "ST001",
  "topic_id": "T101"
}
```

---

## Assessment Item Response

```json
{
  "question_id": "Q001",
  "question": "What is Binary Search?",
  "options": [
    "Option A",
    "Option B",
    "Option C",
    "Option D"
  ],
  "difficulty": "Medium",
  "bloom_level": "Understand"
}
```

---

## Submit Answer Request

```json
{
  "question_id": "Q001",
  "selected_answer": "Option B",
  "response_time": 18
}
```

---

## Assessment Result Response

```json
{
  "score": 8,
  "total": 10,
  "percentage": 80,
  "ability_theta": 0.72,
  "mastery": 0.68
}
```

---

# 7. Learner Profile APIs

## Learner Profile Response

```json
{
  "student_id": "ST001",
  "ability_theta": 0.72,
  "overall_mastery": 0.68,
  "completed_topics": 15,
  "current_topic": "Binary Search"
}
```

---

## Topic Mastery Response

```json
{
  "topic": "Binary Search",
  "mastery": 0.68,
  "status": "Needs Practice"
}
```

---

# 8. Recommendation APIs

## Recommendation Response

```json
{
  "recommendations": [
    {
      "topic": "Binary Search",
      "action": "Practice",
      "priority": 1
    },
    {
      "topic": "Sorting",
      "action": "Review",
      "priority": 2
    }
  ]
}
```

---

# 9. Learning Path APIs

## Learning Path Response

```json
{
  "learning_path": [
    {
      "sequence": 1,
      "topic": "Arrays"
    },
    {
      "sequence": 2,
      "topic": "Binary Search"
    },
    {
      "sequence": 3,
      "topic": "Sorting"
    }
  ]
}
```

---

# 10. AI Tutor APIs

## AI Tutor Request

```json
{
  "topic": "Binary Search",
  "user_message": "Explain with an example."
}
```

---

## AI Tutor Response

```json
{
  "response": "Binary Search is an efficient searching algorithm...",
  "teaching_strategy": "Worked Example",
  "generated_by": "Gemini"
}
```

---

# 11. Analytics APIs

## Progress Response

```json
{
  "overall_progress": 72,
  "completed_topics": 18,
  "remaining_topics": 7,
  "average_mastery": 0.74
}
```

---

## Dashboard Response

```json
{
  "student_name": "John Doe",
  "ability_theta": 0.71,
  "mastery": 0.73,
  "next_recommendation": "Graphs",
  "learning_streak": 12
}
```

---

# 12. Standard API Response Format

Every successful response follows a common structure.

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

---

# 13. Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Topic ID is required."
  }
}
```

---

# 14. HTTP Status Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 201 | Resource Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Resource Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

# 15. Validation Rules

All incoming requests are validated for:

- Required fields
- Data types
- String lengths
- Valid email format
- Enum values
- Numeric ranges
- Authentication tokens

Invalid requests are rejected before reaching business logic.

---

# 16. API Versioning

The API follows URI versioning.

Examples:

```
/api/v1/auth/login

/api/v1/courses

/api/v1/assessments

/api/v1/recommendations

/api/v1/learning-path

/api/v1/ai-tutor
```

Future versions can be introduced without breaking existing clients.

---

# 17. Security Considerations

API communication includes:

- JWT Authentication
- HTTPS encryption
- Role-based authorization
- Input validation
- Output sanitization
- Rate limiting
- Secure error messages

Sensitive learner information is never exposed unnecessarily.

---

# 18. Relationship with System Components

| Component | Uses API Contracts |
|-----------|--------------------|
| React Frontend | Sends requests and receives responses |
| FastAPI Backend | Validates and processes requests |
| Educational Intelligence | Consumes learner and assessment data |
| AI Service Layer | Receives structured teaching context |
| Analytics Module | Retrieves learner progress |

---

# 19. Future Enhancements

Future versions may include:

- GraphQL API
- WebSocket support
- Streaming AI responses
- Bulk assessment submission
- Pagination standards
- OpenAPI auto-generation
- SDK generation for multiple platforms

---

# 20. Summary

The API Data Contracts establish a standardized communication framework for CogniLearn AI by defining consistent request and response structures across authentication, course management, assessments, learner modeling, recommendations, adaptive learning, AI tutoring, and analytics.

By separating API contracts from internal database models, the platform achieves modularity, maintainability, and interoperability while enabling seamless collaboration between the frontend, backend, Educational Intelligence layer, and AI Service Layer.

---

# Guiding Principles

> APIs should expose only the information required by clients.

> Data contracts should remain stable and versioned.

> Validation should occur before business logic execution.

> API responses should be predictable and consistent.

> Internal database models should never be exposed directly.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**