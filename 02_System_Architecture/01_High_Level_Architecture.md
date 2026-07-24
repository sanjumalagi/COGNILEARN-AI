# High Level Architecture
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | High Level Architecture |
| Version | 1.0 |
| Status | Approved Architecture Document |
| Purpose | Define the complete high-level software architecture of CogniLearn AI using the C4 Model |

---

# 1. Introduction

This document presents the high-level architecture of CogniLearn AI using the C4 (Context, Container, Component, Code) architectural model.

The architecture is designed to achieve the following goals:

- Modular software design
- Separation of concerns
- Educational explainability
- AI independence
- Scalability
- Maintainability
- Research reproducibility

Rather than treating Artificial Intelligence as the core of the system, CogniLearn AI treats AI as one component within a larger educational ecosystem.

Educational reasoning remains independent from language generation, allowing future AI technologies to be integrated without redesigning the overall architecture.

---

# 2. Architectural Objectives

The architecture has been designed to satisfy the following objectives.

- Separate educational reasoning from conversational AI
- Maintain modularity between educational services
- Support Learning Outcome–centric learner modeling
- Enable explainable adaptive learning
- Support multiple AI providers
- Allow independent evolution of educational algorithms
- Facilitate future research and experimentation
- Provide a scalable cloud-ready architecture

---

# 3. Architectural Principles

The architecture follows several guiding principles.

## Principle 1

Educational Intelligence drives Teaching Intelligence.

Educational algorithms determine learning decisions before AI generates explanations.

---

## Principle 2

Each architectural layer has a single responsibility.

No layer should perform responsibilities belonging to another layer.

---

## Principle 3

Business logic remains independent of user interface technologies.

Frontend technologies may change without affecting educational intelligence.

---

## Principle 4

Artificial Intelligence is replaceable.

The system must support multiple AI providers through the AI Service Layer.

---

## Principle 5

Educational models remain independent of AI models.

Learner modeling must continue functioning even if AI services are unavailable.

---

## Principle 6

Every educational decision should be explainable through measurable learner evidence.

---

# 4. C4 Level 1 – System Context Diagram

The System Context Diagram identifies the external users and systems interacting with CogniLearn AI.

```
                        +------------------------+
                        |       Teacher          |
                        +-----------+------------+
                                    |
                                    |
                                    v
+------------------+       +-----------------------------+
|   Administrator  |------>|      CogniLearn AI          |<------+
+------------------+       | Intelligent Learning System |       |
                           +-----------------------------+       |
                                    ^                            |
                                    |                            |
                                    |                            |
                           +--------+---------+                  |
                           |      Student     |                  |
                           +------------------+                  |
                                                                 |
                                                                 |
                                                     +-----------+-----------+
                                                     | Google Gemini API     |
                                                     +-----------------------+
```

---

## External Actors

### Student

The primary user of the system.

Responsibilities include:

- Learning
- Attempting assessments
- Viewing analytics
- Receiving adaptive recommendations
- Interacting with AI tutor

---

### Teacher

Responsible for creating educational content.

Responsibilities include:

- Course creation
- Module creation
- Learning Outcome definition
- Assessment Blueprint creation
- Assessment Item Repository management
- Student monitoring

---

### Administrator

Responsible for platform administration.

Responsibilities include:

- User management
- Role management
- System monitoring
- Configuration
- Security management

---

### External AI Provider

Provides natural language generation.

Current provider:

- Google Gemini

Future providers:

- OpenAI
- Claude
- Llama
- Mistral
- DeepSeek

The educational logic remains independent of these providers.

---

# 5. System Boundary

CogniLearn AI includes:

- User Management
- Course Management
- Learning Outcome Management
- Assessment Management
- Learner Modeling
- Adaptive Learning
- AI Tutoring
- Learning Analytics

External systems include:

- AI Providers
- Cloud Storage
- Email Services
- Authentication Providers (future)

---

# 6. C4 Level 2 – Container Diagram

The Container Diagram shows the major deployable parts of the system and how they interact.

```
                        Users
                           │
                           ▼
+--------------------------------------------------+
|              React Web Application               |
| Student Interface                                |
| Teacher Dashboard                                |
| Admin Dashboard                                  |
+----------------------+---------------------------+
                       │ REST API
                       ▼
+--------------------------------------------------+
|               FastAPI Backend                    |
| Authentication                                   |
| Course Management                                |
| Assessment APIs                                  |
| Learner APIs                                     |
| Adaptive APIs                                    |
| AI APIs                                          |
+----------------------+---------------------------+
                       │
                       ▼
+--------------------------------------------------+
|          Educational Intelligence Layer          |
|                                                  |
| Assessment Intelligence                          |
| Learning Intelligence                            |
| Adaptive Intelligence                            |
| Teaching Intelligence                            |
+----------------------+---------------------------+
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
+-------------------+     +-----------------------+
| PostgreSQL        |     | AI Service Layer      |
|                   |     | Prompt Builder        |
|                   |     | Provider Adapter      |
|                   |     | Response Parser       |
+-------------------+     +-----------+-----------+
                                       │
                                       ▼
                              Google Gemini API
```

---

# 7. Container Descriptions

## 7.1 Presentation Layer

Technology:

- React
- TypeScript
- Tailwind CSS

Responsibilities:

- User authentication
- Dashboard rendering
- Assessment interface
- Analytics visualization
- AI tutor interaction

This layer contains no educational logic.

---

## 7.2 Backend Application

Technology:

- FastAPI
- Python

Responsibilities:

- REST APIs
- Authentication
- Authorization
- Request validation
- Business orchestration
- Database communication

The backend coordinates communication between all services.

---

## 7.3 Educational Intelligence Layer

This is the core of CogniLearn AI.

It consists of four independent intelligence modules.

### Assessment Intelligence

Measures learner performance through structured assessments.

---

### Learning Intelligence

Constructs and maintains the learner model using assessment evidence.

---

### Adaptive Intelligence

Generates personalized educational decisions based on learner state.

---

### Teaching Intelligence

Uses AI to communicate educational decisions through explanations, hints, summaries, and feedback.

---

## 7.4 AI Service Layer

The AI Service Layer isolates the application from external AI providers.

Responsibilities include:

- Prompt construction
- Context injection
- Provider abstraction
- Retry mechanisms
- Response validation
- Output parsing
- Logging

This architecture allows future AI providers to be integrated with minimal changes.

---

## 7.5 Database Layer

Technology:

- PostgreSQL
- SQLAlchemy ORM

Responsibilities:

- Persistent storage
- Transaction management
- Learner data
- Educational content
- Assessment records
- Analytics

---

## 7.6 External AI Provider

Current implementation uses Google Gemini.

Future providers may include:

- OpenAI
- Claude
- Llama
- Mistral
- DeepSeek

The AI provider is responsible only for generating educational content, not making educational decisions.

---

# 8. Layered Architecture

The overall system follows a layered architecture.

```
Presentation Layer
        │
        ▼
Application Layer
        │
        ▼
Business Services Layer
        │
        ▼
Educational Intelligence Layer
        │
        ▼
AI Service Layer
        │
        ▼
Infrastructure Layer
```

Each layer communicates only with adjacent layers, ensuring low coupling and high maintainability.

---

# End of Part 1

# 9. C4 Level 3 – Component Diagram

The Component Diagram describes the internal organization of the backend application and illustrates how the major software components collaborate to deliver adaptive learning experiences.

```
                           FastAPI Backend
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
 Authentication             Course Module            Assessment Module
        │                          │                          │
        ├──────────────┬───────────┴──────────────┬───────────┤
        ▼              ▼                          ▼
 Learner Module   Analytics Module         AI Module
        │              │                          │
        └──────────────┼──────────────┬───────────┘
                       ▼              ▼
            Educational Intelligence Layer
                       │
      ┌────────────────┼─────────────────┐
      ▼                ▼                 ▼
Assessment      Learning         Adaptive
Intelligence    Intelligence     Intelligence
      │                │                 │
      └────────────────┼─────────────────┘
                       ▼
             Teaching Intelligence
                       │
                       ▼
               AI Service Layer
                       │
                       ▼
                External AI Provider
```

---

# 10. Component Responsibilities

## 10.1 Authentication Component

Responsible for:

- User registration
- User login
- JWT generation
- Password encryption
- Session validation
- Role authorization

This component provides secure access to every protected endpoint.

---

## 10.2 Course Management Component

Responsible for:

- Course creation
- Module creation
- Topic management
- Learning Outcome management
- Resource management

The component maintains the Knowledge Model.

---

## 10.3 Assessment Component

Responsible for:

- Assessment Blueprint execution
- Assessment generation
- Student response collection
- Assessment scoring
- Assessment history

This component measures learner performance but does not interpret it.

---

## 10.4 Learner Component

Responsible for maintaining learner information.

Functions include:

- Learner profile
- Learning history
- Progress tracking
- Ability records
- Mastery records

This component manages the Learner Model.

---

## 10.5 Analytics Component

Responsible for:

- Performance analytics
- Progress analytics
- Mastery analytics
- Dashboard statistics
- Learning reports

---

## 10.6 AI Module

Responsible for:

- AI tutoring
- Explanation requests
- Hint generation
- Summary generation
- Personalized educational conversations

The AI module communicates only through the AI Service Layer.

---

# 11. Educational Intelligence Components

Educational Intelligence is divided into four independent components.

---

## Assessment Intelligence

Purpose

Measure learning.

Inputs

- Assessment Blueprint
- Student Responses

Outputs

- Assessment Results
- Learning Evidence

Responsibilities

- Assessment execution
- Response evaluation
- Performance measurement

---

## Learning Intelligence

Purpose

Understand learner knowledge.

Inputs

- Assessment Results
- Learning History

Algorithms

- Item Response Theory (IRT)
- Bayesian Knowledge Tracing (BKT)

Outputs

- Learner Profile
- Ability Estimate
- Mastery Estimate

---

## Adaptive Intelligence

Purpose

Generate educational decisions.

Inputs

- Learner Model
- Knowledge Model
- Assessment History

Outputs

- Next Learning Outcome
- Practice Recommendation
- Revision Plan
- Difficulty Recommendation

Adaptive Intelligence never generates educational content.

It only decides what should happen next.

---

## Teaching Intelligence

Purpose

Transform educational decisions into personalized teaching.

Inputs

- Adaptive Decision
- Learner Profile
- Learning Resources

Outputs

- Personalized Explanation
- Examples
- Hints
- Feedback
- Revision Notes

Teaching Intelligence uses Large Language Models but never determines educational strategy.

---

# 12. AI Service Layer Components

The AI Service Layer separates the application from external AI providers.

```
Application
      │
      ▼
AI Service
      │
 ┌────┴────────────────────┐
 ▼                         ▼
Prompt Builder      Response Parser
      │                         │
      └──────────┬──────────────┘
                 ▼
        Provider Adapter
                 │
                 ▼
         Google Gemini API
```

---

## AI Service

Coordinates all AI requests.

Responsibilities

- Context preparation
- Provider selection
- Error handling
- Logging
- Retry logic

---

## Prompt Builder

Constructs prompts using

- Learning Outcomes
- Learner Profile
- Adaptive Decision
- Learning Resources

Prompt Builder ensures educational consistency.

---

## Provider Adapter

Provides abstraction over AI providers.

Current provider

- Google Gemini

Future providers

- OpenAI
- Claude
- Mistral
- Llama
- DeepSeek

---

## Response Parser

Responsible for

- Output validation
- JSON parsing
- Hallucination filtering
- Formatting
- Error recovery

---

# 13. C4 Level 4 – Code Architecture Overview

The software follows a layered package structure.

```
backend/

api/
│
├── auth/
├── users/
├── courses/
├── assessments/
├── analytics/
├── ai/

core/
│
├── config.py
├── security.py
├── dependencies.py

database/
│
├── session.py
├── base.py

models/
│
├── user.py
├── course.py
├── module.py
├── topic.py
├── learning_outcome.py
├── assessment.py
├── learner_profile.py

repositories/
│
├── user_repository.py
├── assessment_repository.py
├── learner_repository.py

services/
│
├── assessment/
├── learner/
├── adaptive/
├── analytics/
├── ai/

algorithms/
│
├── irt/
├── bkt/
├── adaptive_engine/

main.py
```

---

# 14. Dependency Direction

The architecture follows one-way dependency flow.

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

Infrastructure

↓

Database
```

Lower layers never depend on higher layers.

This minimizes coupling and simplifies maintenance.

---

# 15. Architectural Benefits

The component architecture provides the following benefits.

## Educational Benefits

- Learning Outcome–centric learning
- Explainable recommendations
- Evidence-based personalization
- Continuous learner modeling

---

## Technical Benefits

- Modular design
- Independent services
- AI provider abstraction
- Maintainable codebase
- Cloud scalability

---

## Research Benefits

- Reproducible experiments
- Algorithm replacement
- Comparative studies
- Future research extensions

# 16. End-to-End Request Flow

The following sequence illustrates how a learner interacts with the system during a personalized learning session.

```
Student
    │
    ▼
React Web Application
    │
    ▼
FastAPI Backend
    │
    ▼
Authentication Service
    │
    ▼
Assessment Service
    │
    ▼
Educational Intelligence
    │
 ┌──┴───────────────┐
 ▼                  ▼
IRT               BKT
 │                  │
 └──────┬───────────┘
        ▼
Learner Model
        │
        ▼
Adaptive Intelligence
        │
        ▼
Educational Decision
        │
        ▼
AI Service Layer
        │
        ▼
Prompt Builder
        │
        ▼
Google Gemini
        │
        ▼
Response Parser
        │
        ▼
Student
```

The request flow ensures that every AI-generated explanation is based on measurable learner evidence rather than generic prompts.

---

# 17. End-to-End Learning Workflow

The educational workflow follows a structured pipeline from course creation to personalized learning.

```
Teacher Creates Course
        │
        ▼
Create Modules
        │
        ▼
Define Topics
        │
        ▼
Define Learning Outcomes
        │
        ▼
Upload Learning Resources
        │
        ▼
Create Assessment Blueprint
        │
        ▼
Populate Assessment Item Repository
        │
        ▼
Student Attempts Assessment
        │
        ▼
Assessment Results
        │
        ▼
Learning Intelligence
        │
        ▼
Update Learner Model
        │
        ▼
Adaptive Intelligence
        │
        ▼
Educational Recommendation
        │
        ▼
Teaching Intelligence
        │
        ▼
Personalized Learning Experience
        │
        ▼
Updated Learner Progress
```

This workflow repeats continuously throughout the learner's journey, enabling adaptive and personalized education.

---

# 18. Data Flow Architecture

The system processes educational data through a structured pipeline.

```
Educational Content
        │
        ▼
Knowledge Model
        │
        ▼
Assessment
        │
        ▼
Student Responses
        │
        ▼
Assessment Evidence
        │
        ▼
Learner Model
        │
        ▼
Adaptive Engine
        │
        ▼
Educational Decision
        │
        ▼
AI Service Layer
        │
        ▼
Teaching Intelligence
        │
        ▼
Student Feedback
```

Each stage transforms educational information into increasingly personalized learning experiences.

---

# 19. Cross-Cutting Concerns

The following architectural concerns apply across all system components.

## Security

- JWT Authentication
- Password Hashing
- Role-Based Access Control (RBAC)
- Secure API Communication
- Input Validation

---

## Logging

System events are logged to support monitoring and debugging.

Examples include:

- User authentication
- Assessment submissions
- AI requests
- Adaptive recommendations
- System errors

---

## Error Handling

The system implements centralized exception handling to ensure graceful recovery.

Examples include:

- Authentication failures
- Database errors
- Validation errors
- AI provider failures
- Network timeouts

---

## Monitoring

System health is monitored through:

- API performance metrics
- Database performance
- AI response latency
- Error rates
- Resource utilization

---

## Scalability

The architecture supports future horizontal scaling through:

- Stateless backend services
- Independent AI Service Layer
- Modular educational services
- Containerized deployment

---

# 20. Architectural Decisions

The following design decisions guide the implementation of CogniLearn AI.

---

## AD-01

Educational Intelligence is independent of Large Language Models.

Reason:

Educational reasoning should remain deterministic, explainable, and evidence-based.

---

## AD-02

Learning Outcomes are the fundamental educational unit.

Reason:

Learning Outcomes provide measurable and reusable knowledge components for assessment, learner modeling, and adaptive learning.

---

## AD-03

The AI Service Layer abstracts external AI providers.

Reason:

This enables future migration to different LLM providers without affecting application logic.

---

## AD-04

Assessment precedes adaptation.

Reason:

Adaptive recommendations must always be based on measurable learner evidence.

---

## AD-05

Business logic remains independent of presentation technologies.

Reason:

Frontend technologies may evolve without impacting backend functionality.

---

## AD-06

Educational services are modular.

Reason:

Each service can evolve independently, improving maintainability and extensibility.

---

## AD-07

Database access is encapsulated within repository classes.

Reason:

Separating persistence logic from business logic simplifies testing and maintenance.

---

## AD-08

Algorithms are isolated from application services.

Reason:

IRT, BKT, and future educational algorithms can be updated or replaced independently.

---

# 21. Architectural Quality Attributes

The architecture has been designed to satisfy the following quality attributes.

| Attribute | Description |
|------------|-------------|
| Modularity | Independent components with clear responsibilities |
| Scalability | Supports increasing users and educational content |
| Maintainability | Easy to update and extend |
| Explainability | Educational decisions are evidence-based |
| Reliability | Robust handling of failures and exceptions |
| Extensibility | New algorithms and AI providers can be integrated |
| Reusability | Components can be reused across future projects |
| Security | Authentication, authorization, and secure communication |

---

# 22. Future Architectural Extensions

The architecture has been designed to support future enhancements without significant redesign.

Potential extensions include:

- Deep Knowledge Tracing (DKT)
- Knowledge Graph Integration
- Retrieval-Augmented Generation (RAG)
- Multi-Agent Educational Systems
- Explainable AI (XAI)
- Reinforcement Learning for Adaptive Learning
- Speech-Based Tutoring
- Mobile Learning Applications
- Offline Learning Support
- Predictive Learning Analytics

The modular structure ensures that these features can be integrated incrementally.

---

# 23. Architecture Summary

CogniLearn AI adopts a layered, modular, and research-oriented software architecture that separates educational reasoning from artificial intelligence.

The architecture is organized around three core models:

- Knowledge Model
- Learner Model
- Teaching Model

Educational decision-making is implemented through four intelligence layers:

- Assessment Intelligence
- Learning Intelligence
- Adaptive Intelligence
- Teaching Intelligence

An AI Service Layer isolates the application from external AI providers, ensuring long-term flexibility and maintainability.

By emphasizing explainability, modularity, and evidence-based personalization, the architecture provides a strong foundation for intelligent learning, future research, and scalable deployment.

---

# Guiding Architectural Principles

> Measure learning before modeling it.

> Model learning before adapting it.

> Adapt learning before teaching it.

> Teach using evidence rather than assumptions.

These principles govern every architectural decision within CogniLearn AI and ensure that educational intelligence remains the foundation of personalized AI-assisted learning.

---
**End of Document**