# Scope and Requirements
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Scope and Requirements |
| Version | 1.0 |
| Status | Approved Foundation Document |
| Purpose | Define the functional boundaries, system requirements, and implementation scope of CogniLearn AI |

---

# 1. Introduction

This document defines the functional scope, system boundaries, stakeholders, requirements, assumptions, and constraints of CogniLearn AI.

The objective is to clearly establish what the system is expected to accomplish, what features are included within the current implementation roadmap, and which capabilities are intentionally excluded from the project's scope.

The scope defined in this document serves as the foundation for architectural design, software implementation, testing, and future research extensions.

---

# 2. Project Scope

CogniLearn AI is an Intelligent AI Learning Companion that combines educational assessment, learner modeling, adaptive learning, and AI-assisted tutoring within a modular and explainable architecture.

The platform supports the complete educational cycle from structured assessment creation to personalized learning recommendations.

The system is designed around four intelligence layers:

- Assessment Intelligence
- Learning Intelligence
- Adaptive Intelligence
- Teaching Intelligence

Each layer performs a distinct responsibility while collaborating to provide personalized learning experiences.

---

# 3. In Scope

The following capabilities are included within the scope of CogniLearn AI.

---

## 3.1 User Management

The system shall support:

- Student registration
- Teacher registration
- Administrator management
- Secure authentication
- Role-based authorization
- User profile management

---

## 3.2 Course Management

Teachers shall be able to:

- Create courses
- Organize modules
- Create topics
- Define Learning Outcomes (LOs)
- Update course information
- Archive courses

Learning Outcomes represent the smallest assessable educational unit.

---

## 3.3 Learning Resource Management

Teachers shall be able to:

- Upload learning materials
- Organize resources by topic
- Associate resources with Learning Outcomes
- Manage educational content

Supported resources may include:

- PDF documents
- PowerPoint presentations
- Notes
- Images
- Reference links

Future versions may support additional content formats.

---

## 3.4 Assessment Blueprint

Teachers shall be able to create structured Assessment Blueprints that define:

- Learning Outcomes
- Bloom's Taxonomy levels
- Question difficulty
- Number of questions
- Assessment objectives
- Assessment weightage

The Assessment Blueprint serves as the educational specification for all assessments.

---

## 3.5 Assessment Management

The platform shall support:

- Static assessments
- Assessment scheduling
- Student attempts
- Automatic response collection
- Result storage
- Assessment history

Future versions may support adaptive assessments.

---

## 3.6 Learner Modeling

The platform shall maintain a persistent learner model containing:

- Assessment history
- Learning progression
- Learning Outcome mastery
- Topic mastery
- Ability estimation
- Knowledge state

The learner model continuously evolves with every assessment.

---

## 3.7 Psychometric Analysis

The platform shall support:

### Item Response Theory (IRT)

For:

- learner ability estimation
- item difficulty estimation
- educational analytics

### Bayesian Knowledge Tracing (BKT)

For:

- mastery estimation
- knowledge progression
- concept-level learning analysis

These algorithms provide the evidence base for adaptive learning.

---

## 3.8 Adaptive Learning

The Adaptive Intelligence layer shall determine:

- next Learning Outcome
- revision recommendations
- learning sequence
- assessment difficulty
- practice recommendations
- personalized learning path

Educational decisions shall remain explainable and reproducible.

---

## 3.9 AI-Assisted Tutoring

Large Language Models shall provide:

- personalized explanations
- hints
- examples
- summaries
- revision notes
- conversational tutoring
- motivational feedback

The LLM shall communicate educational decisions but shall not determine them.

---

## 3.10 Learning Analytics

The system shall generate analytics for:

Students

- learning progress
- mastery
- assessment history
- strengths
- weaknesses

Teachers

- class performance
- Learning Outcome mastery
- assessment statistics
- learner analytics

Administrators

- platform usage
- course statistics
- system reports

---

# 4. Out of Scope

The following capabilities are intentionally excluded from the current implementation.

- Online proctoring
- Video conferencing
- Virtual classrooms
- Attendance management
- Fee management
- Student admissions
- Payroll systems
- Institution ERP integration
- Certificate generation
- Multiplayer collaborative learning
- Parent portals
- Offline mobile synchronization

These features may be considered in future versions but are not required for the current project.

---

# 5. Functional Requirements

The system shall satisfy the following functional requirements.

---

## FR-01

User authentication and authorization.

---

## FR-02

Role-based access control.

---

## FR-03

Course creation and management.

---

## FR-04

Module management.

---

## FR-05

Topic management.

---

## FR-06

Learning Outcome creation and management.

---

## FR-07

Learning resource upload and organization.

---

## FR-08

Assessment Blueprint creation.

---

## FR-09

Question Bank management.

---

## FR-10

Static assessment generation.

---

## FR-11

Assessment execution.

---

## FR-12

Student response collection.

---

## FR-13

Assessment history management.

---

## FR-14

Learner profile generation.

---

## FR-15

IRT-based learner ability estimation.

---

## FR-16

BKT-based mastery estimation.

---

## FR-17

Adaptive learning recommendation generation.

---

## FR-18

Personalized AI tutoring.

---

## FR-19

Student learning analytics.

---

## FR-20

Teacher learning analytics.

---

# 6. Non-Functional Requirements

The platform shall satisfy the following quality attributes.

---

## Performance

The platform should provide responsive interactions for normal classroom usage.

---

## Scalability

The architecture should support future expansion without significant redesign.

---

## Maintainability

Modules should be independently maintainable.

---

## Reliability

Educational data shall remain consistent and recoverable.

---

## Security

The platform shall implement:

- authentication
- authorization
- password encryption
- secure APIs
- protected learner data

---

## Usability

Interfaces should remain intuitive for students and teachers with minimal training.

---

## Extensibility

Future algorithms, AI models, and educational techniques should be integrated without architectural changes.

---

## Explainability

Every adaptive educational recommendation should be traceable to learner evidence.

---

# 7. Stakeholders

The primary stakeholders are:

Students

Receive personalized learning experiences.

Teachers

Design educational content and monitor learner progress.

Administrators

Manage the platform and users.

Researchers

Evaluate adaptive learning algorithms and learner models.

Developers

Extend and maintain the platform.

---

# 8. Assumptions

The project assumes that:

- teachers define accurate Learning Outcomes
- educational resources align with Learning Outcomes
- learners attempt assessments honestly
- sufficient assessment data exists for learner modeling
- AI services remain available
- internet connectivity exists during normal operation

---

# 9. Constraints

Current implementation constraints include:

- Static assessments in the initial milestone
- Single-institution deployment
- Web-based platform
- English language support
- Limited AI API usage based on available quotas
- Incremental implementation roadmap

These constraints may be relaxed in future versions.

---

# 10. Success Criteria

The project will be considered successful if it demonstrates:

✓ Structured Assessment Blueprint creation

✓ Learning Outcome–centric assessments

✓ Persistent learner modeling

✓ Item Response Theory integration

✓ Bayesian Knowledge Tracing integration

✓ Explainable adaptive learning

✓ Personalized AI tutoring

✓ Comprehensive learning analytics

✓ Modular architecture

✓ Research readiness

---

# 11. Future Scope

Future releases may include:

- Adaptive assessments
- Automatic question generation
- Multi-language support
- Knowledge graphs
- Semantic search
- Vector databases
- Multi-agent tutoring
- Voice-based tutoring
- OCR-based document understanding
- Collaborative learning
- Predictive learning analytics
- Learning style adaptation
- Institution-wide deployment
- Mobile applications

The modular architecture has been designed to accommodate these extensions without requiring major architectural changes.

---

# Scope Statement

CogniLearn AI focuses on creating an explainable, modular, and research-oriented Intelligent AI Learning Companion that integrates structured educational assessment, evidence-based learner modeling, adaptive educational decision-making, and AI-assisted tutoring into a unified educational platform.

The current scope prioritizes educational correctness, research reproducibility, and architectural scalability over feature quantity, ensuring that the platform serves as both a high-quality software system and a foundation for future research and innovation.