# Entity Relationship Model
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Entity Relationship Model |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the conceptual, logical, and physical relationships among the database entities supporting the CogniLearn AI platform. |

---

# 1. Introduction

The Entity Relationship (ER) Model defines the relationships among the core entities of the CogniLearn AI database. It provides a visual and conceptual representation of how learner information, educational content, assessments, adaptive learning components, and AI interactions are interconnected.

The ER model complements the Database Schema by illustrating entity relationships, cardinality, and data dependencies without focusing on implementation details.

---

# 2. Objectives

The Entity Relationship Model aims to:

- Visualize database relationships.
- Represent educational entities.
- Define cardinality between entities.
- Support database implementation.
- Ensure referential integrity.
- Simplify database maintenance.
- Provide a clear blueprint for developers.

---

# 3. ER Modeling Principles

The ER model follows these principles:

### Normalized Design

Each entity represents one educational concept.

---

### Clear Relationships

Relationships reflect real educational workflows.

---

### Minimal Redundancy

Duplicate information is avoided.

---

### High Cohesion

Related data remains within the same entity.

---

### Loose Coupling

Entities communicate through foreign keys.

---

# 4. Conceptual Entity Relationship Diagram

```
                    +----------------+
                    |      User      |
                    +----------------+
                           |
             +-------------+-------------+
             |                           |
             ▼                           ▼
    +----------------+          +----------------+
    | StudentProfile |          | TeacherProfile |
    +----------------+          +----------------+
             |
             ▼
    +----------------+
    | LearnerProfile |
    +----------------+
```

The User entity represents authenticated users, while Student and Teacher profiles extend user-specific information.

---

# 5. Course Structure ER Diagram

```
Course
   │
   │ 1
   │
   │ N
Module
   │
   │ 1
   │
   │ N
Topic
   │
   ├──────────────┐
   │              │
   ▼              ▼
Learning      Assessment
Objective         │
                  ▼
          AssessmentItem
                  │
                  ▼
         AssessmentResponse
```

This hierarchy organizes educational content from courses to assessment responses.

---

# 6. Learner Modeling ER Diagram

```
StudentProfile
       │
       ▼
LearnerProfile
       │
       ├───────────────┐
       │               │
       ▼               ▼
TopicMastery     ProgressHistory
       │
       ▼
Recommendation
       │
       ▼
LearningPath
```

The learner model stores educational progress used by the adaptive algorithms.

---

# 7. Educational Intelligence ER Diagram

```
AssessmentResponse
          │
          ▼
      IRT Engine
          │
          ▼
      BKT Engine
          │
          ▼
    LearnerProfile
          │
          ▼
 Recommendation
          │
          ▼
 LearningPath
          │
          ▼
AdaptiveDecision
          │
          ▼
TeachingContext
```

Although these components represent software modules rather than database tables, the diagram illustrates the flow of educational information through the platform.

---

# 8. AI Interaction ER Diagram

```
TeachingContext
        │
        ▼
AIInteraction
        │
        ▼
AI Provider
```

Each teaching context may generate one or more AI interactions depending on the selected provider.

---

# 9. Logical ER Diagram

```
User
│
├────────────── StudentProfile
│                    │
│                    ▼
│             LearnerProfile
│                    │
│       ┌────────────┼────────────┐
│       ▼            ▼            ▼
│ TopicMastery Recommendation ProgressHistory
│       │            │
│       ▼            ▼
│   LearningPath  TeachingContext
│                     │
│                     ▼
│               AIInteraction
│
Course
│
▼
Module
│
▼
Topic
│
├───────────── LearningObjective
│
└───────────── Assessment
                    │
                    ▼
             AssessmentItem
                    │
                    ▼
           AssessmentResponse
```

---

# 10. Relationship Cardinality

| Relationship | Cardinality |
|--------------|-------------|
| User → Student Profile | One-to-One |
| User → Teacher Profile | One-to-One |
| Course → Module | One-to-Many |
| Module → Topic | One-to-Many |
| Topic → Learning Objective | One-to-Many |
| Topic → Assessment | One-to-Many |
| Assessment → Assessment Item | One-to-Many |
| Assessment Item → Assessment Response | One-to-Many |
| Student → Learner Profile | One-to-One |
| Learner Profile → Topic Mastery | One-to-Many |
| Learner Profile → Recommendation | One-to-Many |
| Learner Profile → Learning Path | One-to-Many |
| Learner Profile → Progress History | One-to-Many |
| Teaching Context → AI Interaction | One-to-Many |

---

# 11. Primary Keys

| Entity | Primary Key |
|----------|-------------|
| User | user_id |
| Student Profile | student_id |
| Teacher Profile | teacher_id |
| Course | course_id |
| Module | module_id |
| Topic | topic_id |
| Learning Objective | objective_id |
| Assessment | assessment_id |
| Assessment Item | item_id |
| Assessment Response | response_id |
| Learner Profile | learner_profile_id |
| Topic Mastery | mastery_id |
| Recommendation | recommendation_id |
| Learning Path | path_id |
| Teaching Context | context_id |
| AI Interaction | interaction_id |
| Progress History | progress_id |

---

# 12. Foreign Keys

| Child Entity | Foreign Key |
|--------------|-------------|
| Student Profile | user_id |
| Teacher Profile | user_id |
| Module | course_id |
| Topic | module_id |
| Learning Objective | topic_id |
| Assessment | topic_id |
| Assessment Item | assessment_id |
| Assessment Response | item_id, student_id |
| Learner Profile | student_id |
| Topic Mastery | learner_profile_id, topic_id |
| Recommendation | student_id, topic_id |
| Learning Path | student_id, topic_id |
| Teaching Context | student_id, topic_id |
| AI Interaction | context_id |
| Progress History | student_id, topic_id |

---

# 13. Relationship with Previous Phases

The Entity Relationship Model connects directly with earlier documentation.

| Previous Phase | Contribution |
|----------------|--------------|
| Project Foundation | Defines educational requirements |
| System Architecture | Defines system components |
| Software Design | Defines services and repositories |
| Algorithm Design | Defines learner modeling algorithms |
| Database Schema | Defines entities and attributes |
| Entity Relationship Model | Defines relationships among entities |

---

# 14. Benefits

The ER model provides:

- Clear visualization of database structure.
- Simplified implementation.
- Improved maintainability.
- Strong referential integrity.
- Better scalability.
- Easier debugging.
- Consistent educational data organization.

---

# 15. Summary

The Entity Relationship Model provides the structural blueprint of the CogniLearn AI database by defining how educational entities are connected throughout the platform. It complements the Database Schema by visualizing relationships, cardinality, and dependencies among learners, educational content, assessments, adaptive learning components, and AI interactions.

This model serves as the foundation for implementing a scalable and maintainable relational database that supports the Educational Intelligence layer.

---

# Guiding Principles

> Every relationship should represent a meaningful educational interaction.

> Referential integrity is essential for adaptive learning.

> Database relationships should remain modular and scalable.

> Entity relationships should mirror the educational workflow.

> Well-designed relationships enable reliable Educational Intelligence.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**