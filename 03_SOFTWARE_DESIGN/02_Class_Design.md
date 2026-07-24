# Class Design
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Class Design |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the major software classes, their responsibilities, relationships, attributes, and operations used to implement the CogniLearn AI platform. |

---

# 1. Introduction

The Class Design defines the primary software classes responsible for implementing the business logic of the CogniLearn AI platform.

Unlike the database models, which represent persistent data, these classes encapsulate the application's behavior and coordinate interactions between the user interface, educational intelligence, adaptive learning algorithms, AI services, and data repositories.

This document serves as the implementation blueprint for the backend services.

---

# 2. Objectives

The Class Design aims to:

- Define major software classes.
- Assign clear responsibilities to each class.
- Promote high cohesion and loose coupling.
- Separate business logic from persistence.
- Improve maintainability.
- Support modular implementation.
- Facilitate unit testing.
- Simplify future extensions.

---

# 3. Class Design Principles

The software classes follow these principles:

- Single Responsibility Principle
- Separation of Concerns
- Interface-Oriented Design
- Dependency Injection
- Composition over Inheritance
- High Cohesion
- Low Coupling

Each class performs one primary responsibility.

---

# 4. High-Level Class Organization

```
Controllers

        │

        ▼

Services

        │

        ▼

Adaptive Intelligence

        │

        ▼

AI Service

        │

        ▼

Repositories

        │

        ▼

Database
```

---

# 5. Core Business Classes

The major software classes are grouped into functional categories.

- Assessment Classes
- Learner Classes
- Adaptive Intelligence Classes
- AI Service Classes
- Analytics Classes
- Repository Classes

---

# 6. Assessment Classes

---

## AssessmentService

### Responsibility

Manages the complete assessment lifecycle.

### Major Operations

- createAssessment()
- generateAssessment()
- submitAssessment()
- evaluateAssessment()
- calculateScore()

### Collaborates With

- AssessmentRepository
- AdaptiveDecisionEngine
- LearnerService

---

## AssessmentRepository

### Responsibility

Provides persistence for assessments.

### Major Operations

- save()
- findById()
- findByTopic()
- update()
- delete()

---

# 7. Learner Classes

---

## LearnerService

### Responsibility

Maintains learner profiles and learning progress.

### Major Operations

- getLearner()
- updateTheta()
- updateMastery()
- recordLearningHistory()
- getWeakConcepts()

### Collaborates With

- LearnerRepository
- IRT Engine
- BKT Engine

---

## LearnerRepository

### Responsibility

Stores and retrieves learner information.

### Major Operations

- save()
- find()
- update()
- delete()

---

# 8. Adaptive Intelligence Classes

---

## AdaptiveDecisionEngine

### Responsibility

Produces personalized educational decisions.

### Major Operations

- determineDifficulty()
- nextLearningOutcome()
- recommendRevision()
- generateLearningPath()
- createAdaptiveDecision()

### Collaborates With

- IRT Engine
- BKT Engine
- Recommendation Engine
- Teaching Engine

---

## IRTEngine

### Responsibility

Estimates learner ability.

### Major Operations

- estimateAbility()
- updateTheta()
- selectDifficulty()

---

## BKTEngine

### Responsibility

Estimates learner knowledge mastery.

### Major Operations

- updateMastery()
- estimateKnowledge()
- predictSuccess()

---

## RecommendationEngine

### Responsibility

Generates personalized learning recommendations.

### Major Operations

- recommendPractice()
- recommendRevision()
- recommendResources()

---

# 9. Teaching Intelligence Classes

---

## TeachingEngine

### Responsibility

Converts educational decisions into teaching instructions.

### Major Operations

- generateTeachingContext()
- requestExplanation()
- generateHint()
- generateSummary()

### Collaborates With

- AIService
- PromptBuilder

---

# 10. AI Service Classes

---

## AIService

### Responsibility

Acts as the gateway between the application and external AI providers.

### Major Operations

- sendPrompt()
- receiveResponse()
- validateResponse()
- parseResponse()

---

## PromptBuilder

### Responsibility

Constructs structured prompts for the AI model.

### Major Operations

- buildExplanationPrompt()
- buildHintPrompt()
- buildSummaryPrompt()

---

## ResponseParser

### Responsibility

Validates and converts AI responses into application-friendly objects.

### Major Operations

- parse()
- validate()
- sanitize()

---

# 11. Analytics Classes

---

## AnalyticsService

### Responsibility

Generates learning analytics and progress reports.

### Major Operations

- generateDashboard()
- calculateProgress()
- topicStatistics()
- learnerStatistics()

---

# 12. Repository Classes

Repositories isolate persistence from business logic.

Major repositories include:

- LearnerRepository
- AssessmentRepository
- CourseRepository
- TopicRepository
- AnalyticsRepository

Repositories expose CRUD operations while hiding database implementation details.

---

# 13. Class Relationships

```
Controller

        │

        ▼

AssessmentService

        │

        ▼

AdaptiveDecisionEngine

        │

        ▼

TeachingEngine

        │

        ▼

AIService

        │

        ▼

Gemini Provider
```

Repositories communicate with the database independently of business services.

---

# 14. Dependency Rules

The following dependency rules are enforced:

- Controllers depend on Services.
- Services depend on Repositories.
- Adaptive Engine depends on educational algorithms.
- AI interactions occur only through AIService.
- Repositories access the database.
- Business services never execute SQL directly.

These rules ensure modularity and maintainability.

---

# 15. Benefits

The Class Design provides:

- Modular implementation
- Clear responsibility boundaries
- Improved maintainability
- Easier testing
- Better scalability
- Simplified debugging
- Reduced coupling
- Future extensibility

---

# 16. Summary

The Class Design defines the primary business classes responsible for implementing the CogniLearn AI platform. Each class has a clearly defined responsibility and collaborates with other classes through well-defined interfaces.

By separating educational intelligence, adaptive learning, AI interaction, analytics, and persistence into dedicated classes, the design promotes maintainability, scalability, and clean implementation while remaining consistent with the overall system architecture.

---

# Guiding Principles

> Every class should have one primary responsibility.

> Business logic belongs in services, not controllers.

> Educational reasoning should remain independent of AI providers.

> AI interactions must pass through the AI Service Layer.

> Persistence should be isolated within repository classes.

> Classes should communicate through interfaces rather than concrete implementations.

---

**End of Document**