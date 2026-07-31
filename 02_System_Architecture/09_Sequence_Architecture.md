# Sequence Architecture
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Sequence Architecture |
| Version | 1.0 |
| Status | Approved Architecture Document |
| Purpose | Define the runtime interactions between system components through sequence diagrams and execution workflows. |

---

# 1. Introduction

The Sequence Architecture describes the dynamic interactions between the components of CogniLearn AI during runtime.

While the System Architecture defines the structural organization of the platform, the Sequence Architecture explains how these components collaborate to fulfill user requests and educational workflows.

Each sequence illustrates the chronological exchange of requests, responses, decisions, and data across the Presentation Layer, Application Layer, Adaptive Intelligence Layer, Database Layer, and External AI Services.

The architecture emphasizes:

- Clear interaction between software components
- Educational decision-making before AI invocation
- Separation of concerns
- Traceable request execution
- Modular service collaboration

---

# 2. Objectives

The Sequence Architecture aims to:

- Describe runtime behavior of the system.
- Illustrate communication between architectural layers.
- Demonstrate educational decision workflows.
- Show AI integration without compromising educational reasoning.
- Support implementation and debugging.
- Improve architectural understanding.
- Provide documentation for developers and researchers.
- Enable validation of software interactions.

---

# 3. Sequence Architecture Overview

Every user interaction follows a structured execution flow.

```
User

    │

    ▼

Frontend

    │

    ▼

API Layer

    │

    ▼

Business Services

    │

    ▼

Adaptive Intelligence

    │

    ▼

AI Service Layer

    │

    ▼

Database / AI Provider

    │

    ▼

Response

    │

    ▼

User
```

Educational decisions always occur before any interaction with the Large Language Model.

---

# 4. Sequence Diagram Principles

All sequence diagrams in this document follow the following principles.

---

## 4.1 Chronological Execution

Interactions are shown from top to bottom in the order they occur.

---

## 4.2 Layered Communication

Requests pass through architectural layers.

```
Presentation

↓

API

↓

Service

↓

Repository

↓

Database
```

Components never bypass architectural boundaries.

---

## 4.3 Single Responsibility

Each component performs only one primary responsibility during a sequence.

Examples:

- Authentication validates credentials.
- Assessment Service evaluates assessments.
- Adaptive Intelligence generates educational decisions.
- Teaching Intelligence prepares AI requests.

---

## 4.4 Educational Intelligence First

Educational reasoning always precedes AI communication.

```
Assessment

↓

Learner Model

↓

Adaptive Intelligence

↓

Teaching Intelligence

↓

AI Service

↓

LLM
```

The AI Tutor never determines instructional strategy.

---

# 5. System Participants

The following participants appear throughout the sequence diagrams.

| Participant | Responsibility |
|-------------|----------------|
| Student | Learner interacting with the platform |
| Teacher | Creates courses and assessments |
| Administrator | Platform management |
| React Frontend | User interface |
| FastAPI API Layer | Request routing |
| Authentication Service | Identity management |
| Assessment Service | Assessment processing |
| Learner Service | Learner profile management |
| Adaptive Intelligence Layer | Educational reasoning |
| Teaching Intelligence Layer | Instruction preparation |
| AI Service Layer | AI provider integration |
| PostgreSQL | Persistent storage |
| Google Gemini | AI explanation generation |

---

# 6. User Authentication Sequence

This sequence authenticates a user before granting access to protected resources.

---

## Sequence Overview

```
Student

    │

Enter Credentials

    │

    ▼

React Frontend

    │

POST /login

    ▼

Authentication API

    │

Validate Request

    ▼

Authentication Service

    │

Retrieve User

    ▼

Repository Layer

    │

Query User

    ▼

PostgreSQL

    │

Return User

    ▲

Verify Password

    │

Generate JWT

    │

Return Token

    ▼

React Frontend

    │

Store Token

    ▼

Student Dashboard
```

---

## Sequence Description

1. Student enters login credentials.
2. Frontend sends login request.
3. Authentication API validates the request.
4. Authentication Service retrieves user information.
5. Repository queries PostgreSQL.
6. Password hash is verified.
7. JWT access token is generated.
8. Token is returned to the frontend.
9. Frontend stores the token securely.
10. Student is redirected to the dashboard.

---

# 7. User Registration Sequence

New learners register before accessing the learning platform.

---

## Sequence Overview

```
Student

    │

Registration Form

    ▼

React Frontend

    │

POST /register

    ▼

Authentication API

    │

Validate Input

    ▼

Authentication Service

    │

Check Existing User

    ▼

Repository Layer

    │

PostgreSQL

    │

No Existing User

    ▲

Hash Password

    │

Create Account

    ▼

Repository Layer

    │

Save User

    ▼

PostgreSQL

    │

Success

    ▼

React Frontend

    │

Registration Complete

    ▼

Student
```

---

## Sequence Description

The registration workflow ensures:

- Input validation
- Email uniqueness
- Secure password hashing
- User profile creation
- Confirmation of successful registration

---

# 8. Course Navigation Sequence

Students browse available courses and learning materials.

---

## Sequence Overview

```
Student

    │

Select Course

    ▼

React Frontend

    │

GET /courses/{id}

    ▼

Course API

    │

Course Service

    ▼

Repository Layer

    │

PostgreSQL

    │

Course Data

    ▲

Course Service

    │

JSON Response

    ▼

React Frontend

    │

Display Course

    ▼

Student
```

---

## Sequence Description

The Course Service retrieves:

- Course information
- Modules
- Topics
- Learning Outcomes
- Learning resources

The frontend renders the course hierarchy for learner navigation.

---

# 9. Learning Resource Access Sequence

Learners access instructional materials before attempting assessments.

---

## Sequence Overview

```
Student

    │

Select Learning Resource

    ▼

React Frontend

    │

GET /resources/{id}

    ▼

Resource API

    │

Resource Service

    ▼

Repository Layer

    │

PostgreSQL

    │

Resource Metadata

    ▲

Storage Service

    │

Retrieve File

    ▼

File Storage

    │

Learning Resource

    ▼

React Frontend

    │

Display Resource

    ▼

Student
```

---

## Sequence Description

The sequence retrieves:

- Resource metadata
- File location
- Access permissions
- Learning material

Resources may include:

- PDFs
- PPT presentations
- Images
- Videos
- Notes

---

# 10. Assessment Generation Sequence

The Assessment Generation Sequence creates a personalized assessment for the learner based on the Assessment Blueprint and learner context.

Unlike traditional quiz systems, the assessment generation process follows educational constraints before presenting questions.

---

## Sequence Overview

```
Student

    │

Start Assessment

    ▼

React Frontend

    │

POST /assessment/start

    ▼

Assessment API

    │

Assessment Service

    │

Retrieve Assessment Blueprint

    ▼

Repository Layer

    │

PostgreSQL

    │

Assessment Blueprint

    ▲

Assessment Service

    │

Retrieve Learner Profile

    ▼

Learner Service

    │

Learner State

    ▲

Assessment Service

    │

Generate Assessment

    ▼

Assessment Repository

    │

Retrieve Questions

    ▼

PostgreSQL

    │

Assessment Items

    ▲

Assessment Service

    │

Personalized Assessment

    ▼

React Frontend

    │

Display Assessment

    ▼

Student
```

---

## Sequence Description

Assessment generation includes:

- Loading the Assessment Blueprint
- Retrieving learner context
- Selecting appropriate assessment items
- Applying educational constraints
- Creating a personalized assessment session

The assessment is generated using predefined educational rules rather than AI-generated questions, ensuring consistency, fairness, and alignment with the course curriculum.

---

# Part 1 Summary

Part 1 established the foundational runtime interactions of CogniLearn AI, covering user authentication, registration, course navigation, learning resource access, and assessment generation.

These workflows demonstrate how requests traverse the Presentation Layer, API Layer, Service Layer, Repository Layer, and Database while preserving architectural boundaries and ensuring that educational logic remains independent of AI services.

The subsequent sections build upon these interactions to illustrate assessment evaluation, adaptive intelligence, AI-assisted teaching, analytics, and complete end-to-end learning workflows.

---

# End of Part 1

# 11. Assessment Submission Sequence

After completing an assessment, the learner's responses are evaluated and become new educational evidence for updating the learner model.

Unlike conventional systems that simply calculate a score, CogniLearn AI transforms assessment evidence into adaptive educational decisions.

---

## Sequence Overview

```
Student

    │

Submit Assessment

    ▼

React Frontend

    │

POST /assessment/submit

    ▼

Assessment API

    │

Assessment Service

    │

Validate Submission

    ▼

Repository Layer

    │

Store Assessment Attempt

    ▼

PostgreSQL

    │

Success

    ▲

Assessment Evaluation

    │

Calculate Score

    │

Generate Assessment Result

    ▼

Adaptive Intelligence Layer

    ▼

Return Assessment Result

    ▼

React Frontend

    ▼

Student
```

---

## Sequence Description

The Assessment Submission process performs the following operations:

1. Validate submitted answers.
2. Store assessment attempt.
3. Store individual responses.
4. Calculate assessment score.
5. Generate assessment evidence.
6. Trigger Adaptive Intelligence.

Assessment completion marks the beginning of the adaptive learning process.

---

# 12. Adaptive Intelligence Decision Sequence

This sequence represents the educational reasoning pipeline of CogniLearn AI.

Every personalized recommendation is produced by this workflow before AI is invoked.

---

## Sequence Overview

```
Assessment Evidence

        │

        ▼

Learner State Engine

        │

Update Learner Profile

        ▼

IRT Engine

        │

Estimate Ability (θ)

        ▼

BKT Engine

        │

Estimate Mastery

        ▼

Mastery Engine

        │

Compute Topic Mastery

        ▼

Difficulty Engine

        │

Determine Difficulty

        ▼

Learning Path Engine

        │

Select Next Learning Outcome

        ▼

Revision Engine

        │

Determine Revision Needs

        ▼

Recommendation Engine

        │

Generate Recommendation

        ▼

Adaptive Decision Engine

        │

Educational Decision

        ▼

Teaching Intelligence
```

---

## Decision Description

The Adaptive Intelligence Layer performs:

- Learner state update
- Ability estimation
- Knowledge tracing
- Mastery computation
- Difficulty adaptation
- Learning path generation
- Revision planning
- Recommendation generation
- Educational decision creation

No AI provider is involved in this sequence.

---

# 13. AI Teaching Sequence

After the Adaptive Intelligence Layer produces an educational decision, the Teaching Intelligence Layer prepares personalized instructional support.

---

## Sequence Overview

```
Adaptive Decision

        │

        ▼

Teaching Intelligence

        │

Retrieve Learner Context

        ▼

AI Service Layer

        │

Prompt Builder

        ▼

Context Manager

        │

Provider Adapter

        ▼

Google Gemini

        │

Generate Explanation

        ▼

Response Parser

        │

Validated Response

        ▼

Teaching Intelligence

        │

Personalized Instruction

        ▼

React Frontend

        ▼

Student
```

---

## Sequence Description

The AI Teaching workflow:

1. Receives structured educational decisions.
2. Builds an educational prompt.
3. Adds learner context.
4. Invokes Gemini.
5. Validates AI response.
6. Returns personalized explanation.

The AI Tutor explains the educational decision—it does not generate it.

---

# 14. Learning Analytics Update Sequence

Every learner interaction contributes to the analytics subsystem.

---

## Sequence Overview

```
Assessment Completed

        │

        ▼

Analytics Service

        │

Collect Metrics

        ▼

Repository Layer

        │

Store Analytics

        ▼

PostgreSQL

        │

Update Dashboard Data

        ▼

Analytics API

        │

Dashboard Response

        ▼

React Frontend
```

---

## Analytics Captured

Examples include:

- Assessment score
- Ability progression
- Topic mastery
- Learning Outcome mastery
- Time spent
- Revision frequency
- Learning path progression

---

# 15. Dashboard Loading Sequence

The learner dashboard aggregates information from multiple services.

---

## Sequence Overview

```
Student

    │

Open Dashboard

    ▼

React Frontend

    │

GET /dashboard

    ▼

Dashboard API

    │

Learner Service

    │

Assessment Service

    │

Analytics Service

    │

Adaptive Service

    ▼

Repository Layer

    ▼

PostgreSQL

    ▲

Dashboard Data

    │

Dashboard API

    ▼

React Frontend

    ▼

Student
```

---

## Dashboard Contents

The dashboard displays:

- Current Courses
- Learning Progress
- Topic Mastery
- Assessment Results
- Recommended Learning Outcome
- Revision Recommendations
- AI Learning History

---

# 16. Teacher Assessment Creation Sequence

Teachers create assessments using the Assessment Blueprint.

---

## Sequence Overview

```
Teacher

    │

Create Assessment

    ▼

React Frontend

    │

POST /assessments

    ▼

Assessment API

    │

Assessment Service

    │

Validate Blueprint

    ▼

Repository Layer

    │

Save Assessment

    ▼

PostgreSQL

    │

Assessment Created

    ▼

React Frontend

    ▼

Teacher
```

---

## Description

Assessment creation includes:

- Assessment metadata
- Assessment Blueprint
- Assessment Items
- Learning Outcome mapping
- Difficulty assignment

This ensures assessments align with intended learning outcomes.

---

# 17. AI Explanation Request Sequence

Learners may request additional explanations for a concept.

---

## Sequence Overview

```
Student

    │

Request Explanation

    ▼

React Frontend

    │

POST /ai/explain

    ▼

Teaching Intelligence

    │

Retrieve Educational Decision

    ▼

AI Service Layer

    │

Prompt Builder

    ▼

Gemini

    │

Generate Explanation

    ▼

Response Parser

    │

Teaching Intelligence

    ▼

React Frontend

    ▼

Student
```

---

## Description

Unlike chatbots, the explanation is grounded in:

- Current Learning Outcome
- Topic mastery
- Learner ability
- Adaptive recommendation

This ensures explanations remain educationally relevant.

---

# 18. Error Handling Sequences

The platform gracefully handles runtime failures.

---

## Authentication Failure

```
Login Request

      │

      ▼

Authentication Service

      │

Invalid Credentials

      ▼

Error Response

      ▼

React Frontend

      ▼

Student
```

---

## AI Provider Failure

```
Teaching Intelligence

      │

      ▼

AI Service

      │

Gemini Unavailable

      ▼

Retry Policy

      │

Fallback Response

      ▼

Frontend
```

---

## Database Failure

```
Repository Layer

      │

Database Error

      ▼

Exception Handler

      │

Log Error

      ▼

Standard Error Response

      ▼

Frontend
```

---

# 19. Logout Sequence

Logout invalidates the user's authenticated session.

---

## Sequence Overview

```
Student

    │

Logout

    ▼

React Frontend

    │

POST /logout

    ▼

Authentication API

    │

Invalidate Session

    ▼

Frontend

    │

Remove JWT

    ▼

Login Screen
```

---

## Sequence Description

Logout performs:

- Session invalidation (if applicable)
- Client token removal
- Redirect to login
- Cleanup of local authentication state

---

# Part 2 Summary

Part 2 described the dynamic execution of CogniLearn AI's core educational workflows.

The sequence diagrams demonstrated how assessment evidence flows through the Adaptive Intelligence Layer, how educational decisions are generated independently of AI, how Teaching Intelligence interacts with the AI Service Layer, and how analytics, dashboards, teacher operations, and runtime error handling are orchestrated.

These interactions reinforce the system's guiding principle:

> **Educational Intelligence drives Teaching Intelligence.**

---

# End of Part 2

# 20. End-to-End Learning Session Sequence

This sequence illustrates a complete personalized learning session, beginning with user authentication and ending with updated learner analytics.

It demonstrates how all major architectural layers collaborate to deliver an adaptive learning experience.

---

## Sequence Overview

```
Student

    │

Login

    ▼

Authentication

    │

Dashboard

    ▼

Course Selection

    │

Learning Resources

    ▼

Assessment

    │

Submit Assessment

    ▼

Assessment Evaluation

    │

Adaptive Intelligence

    │

Educational Decision

    ▼

Teaching Intelligence

    │

AI Service Layer

    ▼

Google Gemini

    │

Personalized Explanation

    ▼

Analytics Update

    │

Dashboard Refresh

    ▼

Student
```

---

## Workflow Description

The complete learning session consists of the following stages:

1. User authentication.
2. Dashboard loading.
3. Course selection.
4. Learning resource study.
5. Personalized assessment.
6. Assessment evaluation.
7. Learner model update.
8. Adaptive educational decision.
9. AI-generated instructional explanation.
10. Analytics update.
11. Dashboard refresh with updated learner progress.

This workflow represents the complete educational lifecycle within CogniLearn AI.

---

# 21. AI Request Lifecycle

Unlike conventional AI applications, AI requests in CogniLearn AI originate only after an educational decision has been made.

---

## AI Request Sequence

```
Educational Decision

        │

        ▼

Teaching Intelligence

        │

        ▼

Prompt Builder

        │

        ▼

Context Manager

        │

        ▼

Provider Adapter

        │

        ▼

Google Gemini

        │

        ▼

Response Parser

        │

        ▼

Teaching Intelligence

        │

        ▼

Frontend
```

---

## AI Lifecycle Description

Each AI request follows these stages:

1. Receive educational decision.
2. Retrieve learner context.
3. Build instructional prompt.
4. Send request to the AI provider.
5. Validate response.
6. Format instructional content.
7. Deliver explanation to the learner.

The AI provider never communicates directly with learners or the database.

---

# 22. Cross-Cutting Runtime Interactions

Several supporting services participate throughout multiple sequences.

---

## Authentication

Authentication validates protected requests before business services are executed.

```
Frontend

      │

JWT Token

      ▼

Authentication Middleware

      │

Authorized Request

      ▼

Business Service
```

---

## Logging

Every major interaction generates operational logs.

Examples include:

- User login
- Assessment submission
- Adaptive decisions
- AI requests
- Errors
- Administrative actions

---

## Monitoring

System health is monitored continuously.

Examples:

- API latency
- AI response time
- Database availability
- Error rates
- Concurrent users

---

## Exception Handling

Runtime exceptions follow a centralized workflow.

```
Service

    │

Exception

    ▼

Global Exception Handler

    │

Log Error

    │

Generate Standard Response

    ▼

Frontend
```

This ensures consistent error reporting and prevents exposure of internal implementation details.

---

# 23. Sequence Quality Attributes

The Sequence Architecture is designed to satisfy the following quality attributes.

---

## Traceability

Every request can be traced from the user interface to the database and back.

---

## Modularity

Each service participates only in interactions relevant to its responsibility.

---

## Scalability

Stateless request handling enables multiple backend instances to process requests concurrently.

---

## Reliability

Structured interaction patterns improve fault tolerance and simplify recovery.

---

## Security

Authentication, authorization, and validation occur before sensitive operations.

---

## Maintainability

Well-defined interaction boundaries reduce coupling between services.

---

## Explainability

Educational decisions are generated using explicit reasoning before AI involvement.

---

## Extensibility

Additional educational engines, AI providers, or services can be integrated without redesigning existing interaction flows.

---

# 24. Sequence Architectural Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| SEQ-01 | Layered request execution | Preserves architectural boundaries |
| SEQ-02 | Frontend communicates only with APIs | Improves security and maintainability |
| SEQ-03 | Repository Layer manages all database access | Centralizes persistence logic |
| SEQ-04 | Adaptive Intelligence executes before AI services | Preserves educational integrity |
| SEQ-05 | Teaching Intelligence mediates AI interactions | Keeps AI independent from educational reasoning |
| SEQ-06 | AI Service Layer abstracts external providers | Supports provider independence |
| SEQ-07 | Centralized authentication middleware | Consistent identity verification |
| SEQ-08 | Global exception handling | Standardized error management |
| SEQ-09 | Analytics updated after educational events | Enables continuous learner monitoring |
| SEQ-10 | End-to-end traceable interactions | Supports debugging, auditing, and research reproducibility |

---

# 25. Runtime Interaction Matrix

| Workflow | Authentication | Database | Adaptive Intelligence | AI Service | Analytics |
|----------|:--------------:|:--------:|:---------------------:|:----------:|:---------:|
| Login | ✓ | ✓ | — | — | ✓ |
| Registration | ✓ | ✓ | — | — | — |
| Course Navigation | ✓ | ✓ | — | — | ✓ |
| Resource Access | ✓ | ✓ | — | — | ✓ |
| Assessment Generation | ✓ | ✓ | ✓ | — | — |
| Assessment Submission | ✓ | ✓ | ✓ | — | ✓ |
| Adaptive Decision | ✓ | ✓ | ✓ | — | ✓ |
| AI Explanation | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dashboard Loading | ✓ | ✓ | ✓ | — | ✓ |
| Logout | ✓ | — | — | — | ✓ |

---

# 26. Sequence Architecture Summary

The Sequence Architecture defines the runtime collaboration of all major components within CogniLearn AI.

The interaction model preserves strict architectural boundaries while enabling personalized adaptive learning.

Key characteristics include:

- Layered request processing
- Stateless backend interactions
- Repository-based data access
- Evidence-driven adaptive reasoning
- AI-mediated instructional communication
- Continuous learner analytics
- Secure authentication and authorization
- Centralized exception handling
- Modular service collaboration
- Fully traceable execution paths

Together, these interaction patterns ensure that educational reasoning remains deterministic, explainable, and independent of the Large Language Model.

---

# Sequence Guiding Principles

> Every request should follow defined architectural layers.

> Educational decisions must precede AI interactions.

> Services should communicate only through well-defined interfaces.

> Runtime interactions should remain traceable and reproducible.

> Authentication and authorization should protect all sensitive operations.

> AI services should remain isolated behind the AI Service Layer.

> Cross-cutting concerns such as logging, monitoring, and exception handling should be centralized.

> Sequence diagrams should reflect the actual implementation architecture.

---

**End of Document**