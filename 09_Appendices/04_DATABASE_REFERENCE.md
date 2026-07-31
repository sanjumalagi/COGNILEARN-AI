# Database Reference
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Database Reference |
| Version | 1.0 |
| Status | Approved Appendix |
| Purpose | Provide a comprehensive reference for the CogniLearn AI database architecture, schema, entities, relationships, constraints, indexing strategy, maintenance, and operational guidelines. |

---

# 1. Introduction

The CogniLearn AI database serves as the persistent storage layer of the platform. It stores learner information, educational content, assessment records, mastery estimates, analytics, system configurations, and operational data required by the Educational Intelligence layer.

The database is designed using relational principles to ensure data consistency, integrity, scalability, and maintainability.

---

# 2. Database Overview

| Property | Value |
|----------|-------|
| Database Management System | PostgreSQL |
| Database Model | Relational |
| ORM | SQLAlchemy |
| Migration Framework | Alembic |
| Character Encoding | UTF-8 |
| Transaction Support | ACID Compliant |

The database is optimized for educational applications that require both transactional consistency and analytical reporting.

---

# 3. Database Architecture

```
Frontend

      │

      ▼

FastAPI Backend

      │

      ▼

Repository Layer

      │

      ▼

SQLAlchemy ORM

      │

      ▼

PostgreSQL Database
```

The application accesses the database only through the Repository Layer, ensuring separation of concerns and maintainability.

---

# 4. Schema Overview

The primary schema consists of the following logical domains:

- User Management
- Course Management
- Learning Content
- Assessment Management
- Educational Intelligence
- Analytics
- System Administration

Each domain contains related entities that support a specific aspect of the platform.

---

# 5. Core Entities

| Entity | Purpose |
|---------|---------|
| Users | Stores learner and administrator accounts |
| Courses | Stores available courses |
| Modules | Groups related learning topics |
| Topics | Individual learning concepts |
| Assessments | Tracks assessment sessions |
| Assessment Items | Stores generated or predefined questions |
| Assessment Responses | Stores learner answers |
| Topic Mastery | Maintains learner mastery estimates |
| Learning Recommendations | Stores personalized recommendations |
| Learning History | Records learner activities |

---

# 6. Users Table

Purpose:

Stores authenticated platform users.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| full_name | User's full name |
| email | Unique email address |
| password_hash | Encrypted password |
| role | Student / Instructor / Administrator |
| created_at | Registration timestamp |

Constraints:

- Primary Key on `id`
- Unique constraint on `email`
- NOT NULL on required fields

---

# 7. Courses Table

Purpose:

Stores course information.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| title | Course title |
| description | Course description |
| created_at | Creation timestamp |

Relationships:

- One course contains many modules.

---

# 8. Modules Table

Purpose:

Represents subdivisions of a course.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| course_id | Foreign Key |
| title | Module title |

Relationships:

- Many modules belong to one course.
- One module contains many topics.

---

# 9. Topics Table

Purpose:

Stores educational concepts.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| module_id | Foreign Key |
| topic_name | Topic title |
| difficulty | Default difficulty level |

Relationships:

- Many topics belong to one module.

---

# 10. Assessments Table

Purpose:

Tracks adaptive assessment sessions.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| user_id | Learner |
| topic_id | Assessment topic |
| start_time | Assessment start |
| end_time | Assessment completion |
| theta | IRT ability estimate |

Each assessment belongs to one learner.

---

# 11. Assessment Items Table

Purpose:

Stores assessment questions.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| assessment_id | Foreign Key |
| question | Question text |
| option_a | Choice A |
| option_b | Choice B |
| option_c | Choice C |
| option_d | Choice D |
| correct_answer | Correct option |
| explanation | Educational explanation |

Questions may be generated dynamically while remaining associated with an assessment session.

---

# 12. Assessment Responses Table

Purpose:

Stores learner responses.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| assessment_item_id | Foreign Key |
| selected_option | Learner answer |
| is_correct | Evaluation result |
| response_time | Submission timestamp |

These records support mastery estimation and analytics.

---

# 13. Topic Mastery Table

Purpose:

Stores learner mastery estimates.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| user_id | Learner |
| topic_id | Topic |
| mastery_score | Current mastery |
| updated_at | Last update |

This table is maintained by the Educational Intelligence layer.

---

# 14. Learning Recommendations Table

Purpose:

Stores personalized recommendations.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| user_id | Learner |
| recommendation | Suggested activity |
| priority | Recommendation ranking |
| generated_at | Creation timestamp |

Recommendations are generated by Adaptive Intelligence.

---

# 15. Learning History Table

Purpose:

Maintains a chronological record of learner activity.

Representative fields:

| Column | Description |
|---------|-------------|
| id | Primary Key |
| user_id | Learner |
| activity | Learning event |
| timestamp | Event time |

Learning history supports analytics and progress reporting.

---

# 16. Relationships

Primary relationships include:

```
Users
   │
   ├──────── Assessments
   │              │
   │              ├──── Assessment Items
   │              │
   │              └──── Assessment Responses
   │
   ├──────── Topic Mastery
   │
   ├──────── Learning Recommendations
   │
   └──────── Learning History

Courses
   │
   ▼

Modules
   │
   ▼

Topics
```

These relationships maintain consistency across learner, course, and assessment data.

---

# 17. Constraints

The database enforces:

- Primary Keys.
- Foreign Keys.
- Unique constraints.
- NOT NULL constraints.
- Referential integrity.
- Cascading updates where appropriate.

These constraints ensure data validity and consistency.

---

# 18. Indexing Strategy

Representative indexes include:

| Index | Purpose |
|--------|---------|
| email | Fast user lookup |
| user_id | Learner queries |
| topic_id | Topic filtering |
| course_id | Module lookup |
| assessment_id | Assessment retrieval |
| created_at | Chronological reporting |

Indexes improve query performance while balancing storage overhead.

---

# 19. Transactions

Database operations requiring consistency should execute within transactions.

Typical transactional operations include:

- User registration.
- Assessment submission.
- Mastery updates.
- Recommendation generation.

Transaction support ensures atomic and reliable updates.

---

# 20. Migration Strategy

Schema evolution is managed using Alembic.

Migration process:

```
Schema Change

      │

      ▼

Migration Script

      │

      ▼

Testing

      │

      ▼

Deployment

      │

      ▼

Production Database
```

Every schema modification should be version-controlled and tested.

---

# 21. Backup Considerations

Critical database data includes:

- User accounts.
- Assessment records.
- Mastery estimates.
- Learning history.
- Recommendations.
- System configuration.

Backups should follow the strategy defined in the Deployment and Operations phase.

---

# 22. Maintenance Guidelines

Regular maintenance activities include:

- Index optimization.
- Query performance analysis.
- Backup verification.
- Vacuum and analyze operations.
- Storage monitoring.
- Migration review.
- Integrity validation.

Preventive maintenance ensures long-term database performance.

---

# 23. Relationship with Previous Documentation

| Document | Contribution |
|----------|--------------|
| Data & Model Design | Schema and ER model |
| Implementation Guide | ORM implementation |
| Deployment & Operations | Database deployment and maintenance |
| Database Reference | Operational database handbook |

This appendix consolidates all database-related information into a single reference.

---

# 24. Summary

This document described the CogniLearn AI database architecture, schema, entities, relationships, constraints, indexing strategy, transactions, migration process, backup considerations, and maintenance guidelines.

The relational database design provides a reliable and scalable foundation for learner management, adaptive assessments, Educational Intelligence, analytics, and long-term operational support.

---

# Guiding Principles

> Data integrity should be preserved through strong relational design.

> Database access should occur through the Repository Layer.

> Schema evolution should be controlled through versioned migrations.

> Educational Intelligence data should remain consistent, secure, and auditable.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**