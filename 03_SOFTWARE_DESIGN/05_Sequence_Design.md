# Sequence Design
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Sequence Design |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the interaction sequence between software classes during the execution of major application use cases. |

---

# 1. Introduction

The Sequence Design describes the runtime interactions between software classes during the execution of major use cases within the CogniLearn AI platform.

Unlike the architectural sequence diagrams, which illustrate interactions between system components, the sequence design focuses on method-level communication among controllers, services, repositories, algorithms, and AI services.

These interactions serve as implementation guides for developers and ensure that responsibilities remain clearly distributed across the software layers.

---

# 2. Objectives

The Sequence Design aims to:

- Define runtime interactions between classes.
- Illustrate method invocation order.
- Describe data flow between software layers.
- Clarify software responsibilities.
- Support implementation.
- Improve maintainability.
- Simplify debugging.

---

# 3. Design Principles

The interaction design follows these principles:

- Controllers coordinate requests.
- Services contain business logic.
- Repositories handle persistence.
- Algorithms perform educational reasoning.
- AI Service manages AI communication.
- Layers communicate only through defined interfaces.

---

# 4. Login Sequence

## Participants

- User
- AuthController
- AuthService
- UserRepository
- JWTService

### Interaction

```
User

↓

AuthController.login()

↓

AuthService.authenticate()

↓

UserRepository.findByEmail()

↓

Password Validation

↓

JWTService.generateToken()

↓

Return JWT

↓

Frontend
```

---

# 5. Assessment Generation Sequence

## Participants

- Student
- AssessmentController
- AssessmentService
- AssessmentRepository

### Interaction

```
Student

↓

AssessmentController.generate()

↓

AssessmentService.generateAssessment()

↓

AssessmentRepository.getAssessment()

↓

Return Assessment

↓

Student
```

---

# 6. Assessment Submission Sequence

## Participants

- Student
- AssessmentController
- AssessmentService
- AssessmentRepository
- LearnerService

### Interaction

```
Student

↓

submitAssessment()

↓

AssessmentController

↓

AssessmentService

↓

AssessmentRepository.saveResponses()

↓

AssessmentRepository.calculateScore()

↓

LearnerService.updateHistory()

↓

Return Result
```

---

# 7. Adaptive Decision Sequence

## Participants

- AssessmentService
- LearnerService
- IRTEngine
- BKTEngine
- AdaptiveDecisionEngine

### Interaction

```
AssessmentService

↓

LearnerService

↓

IRTEngine.updateTheta()

↓

BKTEngine.updateMastery()

↓

AdaptiveDecisionEngine.createDecision()

↓

Return Adaptive Decision
```

---

# 8. AI Explanation Sequence

## Participants

- TeachingService
- PromptBuilder
- AIService
- GeminiProvider
- ResponseParser

### Interaction

```
TeachingService

↓

PromptBuilder.buildPrompt()

↓

AIService.generateResponse()

↓

GeminiProvider

↓

ResponseParser.parse()

↓

TeachingService

↓

Student
```

---

# 9. Dashboard Loading Sequence

## Participants

- DashboardController
- AnalyticsService
- AnalyticsRepository

### Interaction

```
Dashboard

↓

DashboardController

↓

AnalyticsService

↓

AnalyticsRepository

↓

Dashboard Data

↓

Dashboard
```

---

# 10. Teacher Assessment Creation Sequence

## Participants

- Teacher
- AssessmentController
- AssessmentService
- AssessmentRepository

### Interaction

```
Teacher

↓

AssessmentController

↓

AssessmentService

↓

AssessmentRepository.save()

↓

Database

↓

Success Response
```

---

# 11. Repository Interaction Pattern

All repositories follow a consistent interaction model.

```
Controller

↓

Service

↓

Repository

↓

Database

↓

Repository

↓

Service

↓

Controller
```

Repositories never contain business logic.

---

# 12. AI Service Interaction Pattern

```
TeachingService

↓

PromptBuilder

↓

AIService

↓

IAIProvider

↓

GeminiProvider

↓

ResponseParser

↓

TeachingService
```

Business services never communicate directly with AI providers.

---

# 13. Adaptive Intelligence Interaction Pattern

```
Assessment Result

↓

LearnerService

↓

IRT Engine

↓

BKT Engine

↓

AdaptiveDecisionEngine

↓

RecommendationEngine

↓

TeachingService
```

Educational reasoning is completed before AI content generation.

---

# 14. Error Handling Sequence

```
Controller

↓

Service

↓

Repository

↓

Exception

↓

GlobalExceptionHandler

↓

HTTP Response
```

All exceptions are propagated through the global exception handling mechanism.

---

# 15. Summary

The Sequence Design defines the method-level interactions between software classes responsible for implementing the CogniLearn AI platform. These interaction sequences describe how requests flow through controllers, services, repositories, adaptive intelligence components, AI services, and persistence layers.

By maintaining clear separation of responsibilities and consistent interaction patterns, the design supports maintainability, scalability, and clean implementation while remaining aligned with the platform's layered architecture.

---

# Guiding Principles

> Controllers coordinate requests but contain no business logic.

> Services implement business rules.

> Repositories manage persistence.

> Adaptive Intelligence performs educational reasoning.

> AI interactions occur exclusively through the AI Service Layer.

> Sequence flows should remain simple, modular, and predictable.

---

**End of Document**