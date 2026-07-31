# Component Architecture
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Component Architecture |
| Version | 1.0 |
| Status | Approved Architecture Document |
| Purpose | Define the internal component architecture of CogniLearn AI and describe the responsibilities and interactions of each major software component. |

---

# 1. Introduction

The Component Architecture defines the internal organization of the CogniLearn AI platform.

Unlike the High-Level Architecture, which focuses on the interaction between major system containers, this document describes the internal software components responsible for implementing the system's business logic.

Each component has a clearly defined responsibility, communicates through well-defined interfaces, and adheres to the principle of separation of concerns.

The architecture follows a modular service-oriented design, enabling independent development, testing, and future extensibility.

---

# 2. Component Architecture Overview

The backend application consists of multiple logical components grouped according to their responsibilities.

```
                    FastAPI Backend

                            │

    ┌───────────────────────┼────────────────────────┐
    │                       │                        │
    ▼                       ▼                        ▼

Authentication      Course Management      Assessment Management

    │                       │                        │

    ├──────────────┬────────┴───────────┬────────────┤
    ▼              ▼                    ▼

Learner       Analytics Service     AI Service

    │              │                    │

    └──────────────┼────────────────────┘
                   ▼

       Educational Intelligence Layer

                   │

    ┌──────────────┼────────────────┐

    ▼              ▼                ▼

Assessment    Learning       Adaptive

Intelligence Intelligence   Intelligence

                   │

                   ▼

          Teaching Intelligence
```

---

# 3. Component Design Principles

Every component follows the same architectural principles.

## Single Responsibility

Each component performs one well-defined task.

Example:

- Authentication handles authentication only.
- Assessment handles assessments only.
- Adaptive Intelligence generates recommendations only.

---

## Loose Coupling

Components communicate through interfaces rather than direct dependencies.

This allows independent modification without affecting the rest of the system.

---

## High Cohesion

Functions within a component are closely related to one another.

---

## Reusability

Components should be reusable by multiple services whenever possible.

---

## Testability

Each component should support independent unit testing.

---

## Extensibility

Future algorithms and services should be integrated without modifying existing components.

---

# 4. Component Interaction

The following diagram illustrates how the major components collaborate.

```
Frontend

    │

    ▼

Authentication

    │

    ▼

Course Management

    │

    ▼

Assessment Management

    │

    ▼

Assessment Intelligence

    │

    ▼

Learning Intelligence

    │

    ▼

Adaptive Intelligence

    │

    ▼

Teaching Intelligence

    │

    ▼

AI Service Layer

    │

    ▼

Gemini API
```

Educational reasoning always occurs before AI interaction.

---

# 5. Authentication Component

## Purpose

Provide secure access to the platform.

---

## Responsibilities

- User Registration
- User Login
- Password Encryption
- JWT Generation
- Token Validation
- Role-Based Authorization
- Session Management

---

## Inputs

- Email
- Password
- User Role

---

## Outputs

- JWT Access Token
- Refresh Token
- Authenticated User

---

## Dependencies

- User Repository
- Security Module
- JWT Library

---

## Public Services

```
register_user()

login_user()

refresh_token()

logout_user()

verify_token()

change_password()
```

---

## Internal Workflow

```
User Credentials

        │

        ▼

Validation

        │

        ▼

Password Verification

        │

        ▼

JWT Generation

        │

        ▼

Authenticated Session
```

---

# 6. User Management Component

## Purpose

Manage student, teacher, and administrator profiles.

---

## Responsibilities

- User Creation
- Profile Management
- Role Assignment
- Account Activation
- Account Deactivation
- User Search
- User Statistics

---

## Managed Entities

- Student
- Teacher
- Administrator

---

## Inputs

- Registration Data
- Profile Updates

---

## Outputs

- User Profile
- User List
- User Statistics

---

## Dependencies

- User Repository
- Authentication Component

---

## Public Services

```
create_user()

update_user()

delete_user()

get_user()

list_users()

assign_role()
```

---

# 7. Course Management Component

## Purpose

Maintain the Knowledge Model.

---

## Responsibilities

- Course Creation
- Module Creation
- Topic Management
- Learning Outcome Management
- Resource Management
- Course Publishing

---

## Knowledge Hierarchy

```
Course

    │

    ▼

Module

    │

    ▼

Topic

    │

    ▼

Learning Outcome

    │

    ▼

Learning Resources

    │

    ▼

Assessment Blueprint
```

---

## Inputs

Teacher requests.

---

## Outputs

Educational content available for learning and assessment.

---

## Managed Entities

- Course
- Module
- Topic
- Learning Outcome
- Learning Resource
- Assessment Blueprint

---

## Dependencies

- Course Repository
- Resource Repository

---

## Public Services

```
create_course()

update_course()

delete_course()

create_module()

create_topic()

create_learning_outcome()

upload_resource()

publish_course()
```

---

## Internal Workflow

```
Teacher

    │

    ▼

Create Course

    │

    ▼

Create Module

    │

    ▼

Create Topic

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

Course Ready
```

---

# 8. Component Relationships

| Component | Depends On |
|------------|------------|
| Authentication | User Repository |
| User Management | Authentication |
| Course Management | Course Repository |
| Assessment Management | Course Management |
| Learning Intelligence | Assessment Management |
| Adaptive Intelligence | Learning Intelligence |
| Teaching Intelligence | Adaptive Intelligence |
| AI Service Layer | Teaching Intelligence |

The dependency direction is strictly one-way to prevent cyclic dependencies and maintain architectural integrity.

---

# End of Part 1

# 9. Assessment Intelligence Component

## Purpose

Assessment Intelligence is responsible for measuring learner knowledge through structured educational assessments.

It represents the first layer of Educational Intelligence and serves as the foundation for learner modeling.

This component does not attempt to personalize learning or generate recommendations. Its responsibility is limited to collecting accurate evidence about learner performance.

---

## Responsibilities

- Assessment Blueprint execution
- Assessment generation
- Assessment scheduling
- Assessment delivery
- Student response collection
- Response validation
- Automatic scoring
- Assessment result storage
- Assessment history management

---

## Inputs

- Assessment Blueprint
- Learning Outcomes
- Assessment Item Repository
- Student Responses

---

## Outputs

- Assessment Scores
- Learning Evidence
- Assessment History
- Learning Outcome Performance

---

## Managed Entities

- Assessment
- Assessment Attempt
- Assessment Item
- Assessment Response
- Assessment Result
- Assessment Blueprint

---

## Internal Workflow

```
Assessment Blueprint

        │

        ▼

Assessment Generation

        │

        ▼

Student Attempts Assessment

        │

        ▼

Collect Responses

        │

        ▼

Automatic Evaluation

        │

        ▼

Store Assessment Evidence

        │

        ▼

Send Results to Learning Intelligence
```

---

## Public Services

```
create_assessment()

start_assessment()

submit_assessment()

evaluate_assessment()

calculate_score()

store_results()

get_assessment_history()
```

---

## Design Principles

Assessment Intelligence measures learning but never interprets learning.

Its only responsibility is producing reliable educational evidence.

---

# 10. Learning Intelligence Component

## Purpose

Learning Intelligence transforms assessment evidence into an evolving learner model.

It estimates learner ability, mastery, strengths, weaknesses, and learning progress using educational algorithms.

This layer answers the question:

**"What does the learner currently know?"**

---

## Responsibilities

- Learner profile management
- Learning history management
- Ability estimation
- Mastery estimation
- Knowledge state tracking
- Weak Learning Outcome detection
- Strong Learning Outcome detection
- Learning analytics

---

## Educational Algorithms

### Item Response Theory (IRT)

Used for estimating learner ability.

Produces:

- Ability (θ)
- Item Difficulty
- Learning Progress

---

### Bayesian Knowledge Tracing (BKT)

Used for estimating mastery.

Produces:

- Probability of Mastery
- Learning Progress
- Knowledge State

---

## Inputs

- Assessment Results
- Assessment History
- Learning Outcomes
- Student Responses

---

## Outputs

- Learner Profile
- Ability Estimate
- Mastery Estimate
- Weak Learning Outcomes
- Strong Learning Outcomes
- Learning History

---

## Managed Entities

- Learner Profile
- Learning History
- Topic Mastery
- Learning Outcome Mastery
- Ability Record

---

## Internal Workflow

```
Assessment Results

        │

        ▼

IRT Calculation

        │

        ▼

BKT Calculation

        │

        ▼

Learner Model Update

        │

        ▼

Store Learning History

        │

        ▼

Send Learner Model to Adaptive Intelligence
```

---

## Public Services

```
update_learner_model()

calculate_theta()

calculate_mastery()

identify_weak_outcomes()

identify_strong_outcomes()

get_learning_history()

get_learner_profile()
```

---

## Design Principles

Learning Intelligence understands learner knowledge but never recommends learning activities.

---

# 11. Adaptive Intelligence Component

## Purpose

Adaptive Intelligence converts learner knowledge into educational decisions.

This component answers the question:

**"What should the learner study next?"**

Adaptive Intelligence does not generate explanations.

It only decides the next educational action.

---

## Responsibilities

- Learning path generation
- Next Learning Outcome selection
- Difficulty adaptation
- Revision planning
- Practice recommendation
- Personalized sequencing
- Adaptive decision generation

---

## Inputs

- Learner Profile
- Ability Estimate
- Mastery Estimate
- Learning History
- Assessment Blueprint
- Knowledge Model

---

## Outputs

- Next Learning Outcome
- Recommended Difficulty
- Revision Topics
- Practice Questions
- Adaptive Learning Plan

---

## Internal Workflow

```
Learner Model

        │

        ▼

Identify Weak Outcomes

        │

        ▼

Prioritize Learning Outcomes

        │

        ▼

Select Next Topic

        │

        ▼

Generate Learning Plan

        │

        ▼

Send Decision to Teaching Intelligence
```

---

## Decision Factors

Adaptive decisions consider:

- Ability Level
- Mastery Probability
- Assessment Performance
- Learning History
- Revision Frequency
- Learning Outcome Priority

---

## Public Services

```
generate_learning_plan()

recommend_next_outcome()

recommend_difficulty()

recommend_revision()

recommend_practice()

generate_adaptive_path()
```

---

## Design Principles

Adaptive Intelligence makes educational decisions but never generates educational content.

---

# 12. Teaching Intelligence Component

## Purpose

Teaching Intelligence transforms educational decisions into personalized learning experiences.

It uses Large Language Models as educational communicators.

This component answers the question:

**"How should the concept be explained?"**

---

## Responsibilities

- Personalized explanations
- Example generation
- Hint generation
- Summary generation
- Feedback generation
- Motivational guidance
- Conversational tutoring

---

## Inputs

- Adaptive Decision
- Learner Profile
- Learning Resources
- Learning Outcome
- Educational Context

---

## Outputs

- Personalized Explanation
- Hints
- Examples
- Revision Notes
- Feedback
- Interactive Tutoring

---

## Internal Workflow

```
Adaptive Decision

        │

        ▼

Prepare Educational Context

        │

        ▼

AI Service Layer

        │

        ▼

Large Language Model

        │

        ▼

Validate Response

        │

        ▼

Deliver Personalized Teaching
```

---

## Public Services

```
generate_explanation()

generate_summary()

generate_hint()

generate_feedback()

generate_examples()

generate_revision_notes()
```

---

## Design Principles

Teaching Intelligence communicates educational decisions but never determines educational strategy.

All teaching content must originate from evidence-based decisions generated by Adaptive Intelligence.

---

# 13. Educational Intelligence Pipeline

The four educational intelligence components work together in a sequential pipeline.

```
Assessment Intelligence

        │

        ▼

Learning Intelligence

        │

        ▼

Adaptive Intelligence

        │

        ▼

Teaching Intelligence

        │

        ▼

Student Learning Experience
```

Each component has a single responsibility, ensuring explainability, modularity, and maintainability.

---

# End of Part 2


# 14. AI Service Layer Component

## Purpose

The AI Service Layer provides a standardized interface between the application and external Large Language Models (LLMs).

It isolates the educational system from provider-specific implementations, ensuring that AI providers can be replaced without affecting the rest of the application.

The AI Service Layer is responsible for communication, prompt construction, response validation, error handling, and provider abstraction.

---

## Responsibilities

- Prompt construction
- Context management
- AI provider selection
- Request validation
- Response parsing
- Retry mechanisms
- Logging
- Error handling
- Provider abstraction

---

## Internal Components

```
AI Service

    │

    ├──────────────┐

    ▼              ▼

Prompt Builder   Provider Adapter

    │              │

    └──────┬───────┘

           ▼

Response Parser

           │

           ▼

External AI Provider
```

---

## AI Service

Acts as the central coordinator for all AI interactions.

Responsibilities:

- Receive requests from Teaching Intelligence
- Build AI requests
- Invoke AI provider
- Validate responses
- Return formatted output

---

## Prompt Builder

Responsible for constructing structured prompts using:

- Learning Outcomes
- Adaptive Decisions
- Learner Profile
- Learning Resources
- Educational Context

The Prompt Builder ensures consistent, explainable, and educationally aligned prompts.

---

## Provider Adapter

Abstracts communication with AI providers.

Current provider:

- Google Gemini

Future providers:

- OpenAI
- Claude
- Mistral
- DeepSeek
- Llama

The remainder of the application never communicates directly with an AI provider.

---

## Response Parser

Responsible for:

- JSON validation
- Response formatting
- Content filtering
- Error detection
- Educational consistency checks

---

## Public Services

```
generate_response()

build_prompt()

send_request()

parse_response()

validate_response()

retry_request()
```

---

# 15. Analytics Component

## Purpose

Provide actionable educational insights for students, teachers, and administrators.

---

## Responsibilities

- Performance analytics
- Learning analytics
- Assessment analytics
- Course analytics
- Progress tracking
- Dashboard generation

---

## Inputs

- Assessment Results
- Learner Profile
- Learning History
- Adaptive Decisions

---

## Outputs

- Student Dashboard
- Teacher Dashboard
- Administrative Reports
- Learning Progress Reports

---

## Public Services

```
generate_dashboard()

student_progress()

teacher_report()

course_statistics()

learning_analytics()

performance_summary()
```

---

# 16. Repository Layer

## Purpose

The Repository Layer manages all communication with the database.

Repositories encapsulate persistence logic and isolate database operations from business logic.

---

## Responsibilities

- CRUD operations
- Query optimization
- Transaction management
- Entity retrieval
- Data persistence

---

## Repository Structure

```
repositories/

├── user_repository.py
├── course_repository.py
├── module_repository.py
├── topic_repository.py
├── learning_outcome_repository.py
├── assessment_repository.py
├── learner_repository.py
├── analytics_repository.py
└── ai_repository.py
```

---

## Benefits

- Database independence
- Improved maintainability
- Easier testing
- Separation of concerns

---

# 17. Component Communication

All components communicate through service interfaces.

```
Frontend

    │

    ▼

REST API

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

Infrastructure
```

Direct communication between unrelated components is prohibited.

This architecture minimizes coupling and improves maintainability.

---

# 18. Dependency Rules

The following dependency rules govern component interactions.

### Rule 1

Presentation components never access the database directly.

---

### Rule 2

Business services never communicate directly with AI providers.

---

### Rule 3

Only the AI Service Layer communicates with external LLMs.

---

### Rule 4

Adaptive Intelligence depends on the Learner Model but not on the Presentation Layer.

---

### Rule 5

Teaching Intelligence depends on Adaptive Intelligence.

---

### Rule 6

Repositories never contain business logic.

---

### Rule 7

Educational algorithms remain isolated inside the Algorithms package.

---

# 19. Error Handling Strategy

Every component implements standardized error handling.

Examples include:

- Authentication failures
- Validation errors
- Database exceptions
- AI provider failures
- Network timeouts
- Missing educational resources

Errors are propagated through centralized exception handlers and logged for monitoring.

---

# 20. Logging Strategy

The system records significant events to support debugging, monitoring, and auditing.

Logged events include:

- User authentication
- Course creation
- Assessment attempts
- Learner model updates
- Adaptive recommendations
- AI requests
- AI responses
- System errors

---

# 21. Security Considerations

Every component follows secure development practices.

Security mechanisms include:

- JWT authentication
- Password hashing
- Role-Based Access Control (RBAC)
- Input validation
- Output sanitization
- Secure API communication
- Environment-based configuration
- Secret management

---

# 22. Component Testing Strategy

Each component supports independent testing.

Testing levels include:

### Unit Testing

Individual services and algorithms.

---

### Integration Testing

Communication between services.

---

### API Testing

REST endpoint validation.

---

### Database Testing

Repository and transaction testing.

---

### AI Testing

Prompt generation, response validation, and parsing.

---

### End-to-End Testing

Complete educational workflows.

---

# 23. Future Component Extensions

The architecture supports future enhancements without requiring major redesign.

Potential extensions include:

- Deep Knowledge Tracing (DKT)
- Knowledge Graph Engine
- Retrieval-Augmented Generation (RAG)
- Multi-Agent Educational Systems
- Reinforcement Learning
- Explainable AI (XAI)
- Speech-Based Tutoring
- Mobile Learning Services
- Recommendation Engine
- Predictive Analytics

Each extension can be integrated as an independent component.

---

# 24. Component Architecture Summary

The Component Architecture of CogniLearn AI provides a modular, maintainable, and research-oriented software structure.

Each component has a clearly defined responsibility and interacts with other components through well-defined interfaces.

The Educational Intelligence Layer forms the core of the platform by separating:

- Assessment Intelligence
- Learning Intelligence
- Adaptive Intelligence
- Teaching Intelligence

The AI Service Layer abstracts all communication with external Large Language Models, ensuring flexibility and long-term maintainability.

This architecture enables scalable implementation, supports educational explainability, and provides a strong foundation for future research and system evolution.

---

# Guiding Principles

> One component. One responsibility.

> Educational Intelligence remains independent of Artificial Intelligence.

> Components communicate through interfaces, not implementations.

> Educational decisions are evidence-based.

> AI enhances teaching but never replaces educational reasoning.

---
**End of Document**