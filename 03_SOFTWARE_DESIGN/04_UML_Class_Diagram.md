# UML Class Diagrams
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | UML Class Diagrams |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Present the structural design of CogniLearn AI through UML class diagrams representing the relationships between the major software components. |

---

# 1. Introduction

The UML Class Diagrams describe the static structure of the CogniLearn AI platform.

These diagrams illustrate:

- Classes
- Interfaces
- Attributes
- Methods
- Relationships
- Dependencies
- Aggregation
- Composition
- Inheritance

Unlike the System Architecture, which describes high-level components, these diagrams describe the internal software structure that guides implementation.

---

# 2. Objectives

The UML diagrams are intended to:

- Visualize software structure
- Define relationships
- Simplify implementation
- Improve maintainability
- Support code generation
- Aid developer understanding

---

# 3. UML Diagram List

This document contains the following diagrams.

| Diagram | Purpose |
|----------|----------|
| Overall System Class Diagram | Complete software structure |
| Domain Model Diagram | Educational entities |
| Service Layer Diagram | Business services |
| Repository Layer Diagram | Data access layer |
| Adaptive Intelligence Diagram | Educational intelligence |
| AI Service Layer Diagram | AI abstraction |
| Authentication Diagram | Security classes |

---

# 4. Overall System Class Diagram

## Purpose

Shows the complete software structure of the platform.

### Includes

- Controllers
- Services
- Repositories
- Models
- AI Service
- Adaptive Engine

**<< Insert UML Diagram >>**

---

# 5. Domain Model Diagram

## Purpose

Shows educational entities.

### Classes

- Course
- Module
- Topic
- LearningOutcome
- Assessment
- AssessmentItem
- Student
- Attempt
- Response
- TopicMastery

**<< Insert UML Diagram >>**

---

# 6. Service Layer Diagram

## Purpose

Shows business logic classes.

### Classes

- AssessmentService
- LearnerService
- AdaptiveService
- TeachingService
- AnalyticsService

**<< Insert UML Diagram >>**

---

# 7. Repository Layer Diagram

## Purpose

Shows persistence classes.

### Classes

- AssessmentRepository
- LearnerRepository
- CourseRepository
- TopicRepository
- AnalyticsRepository

**<< Insert UML Diagram >>**

---

# 8. Adaptive Intelligence Diagram

## Purpose

Illustrates adaptive learning components.

### Classes

- AdaptiveDecisionEngine
- IRTEngine
- BKTEngine
- RecommendationEngine
- LearningPathEngine

**<< Insert UML Diagram >>**

---

# 9. AI Service Layer Diagram

## Purpose

Illustrates AI abstraction.

### Classes

- AIService
- PromptBuilder
- ResponseParser
- IAIProvider
- GeminiProvider

**<< Insert UML Diagram >>**

---

# 10. Authentication Diagram

## Purpose

Illustrates authentication and authorization.

### Classes

- User
- Role
- JWTService
- AuthService

**<< Insert UML Diagram >>**

---

# 11. UML Relationships

The following UML relationships are used.

| Relationship | Description |
|--------------|-------------|
| Association | Communication between classes |
| Aggregation | Weak ownership |
| Composition | Strong ownership |
| Dependency | Uses relationship |
| Realization | Interface implementation |
| Inheritance | Parent-child relationship |

---

# 12. Summary

The UML Class Diagrams provide a detailed visualization of the software structure of CogniLearn AI. They complement the architectural documentation by illustrating the relationships between classes, services, repositories, adaptive intelligence components, AI service abstractions, and domain entities. These diagrams serve as implementation references for developers and support maintainability and future system evolution.

---

**End of Document**