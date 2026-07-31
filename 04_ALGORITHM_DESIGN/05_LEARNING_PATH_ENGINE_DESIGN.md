# Learning Path Engine Design
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Learning Path Engine Design |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the design and implementation of the Learning Path Engine responsible for generating personalized learning sequences based on learner ability, mastery, recommendations, and curriculum structure. |

---

# 1. Introduction

The Learning Path Engine generates personalized learning sequences that guide learners through educational content in an effective and structured manner.

Unlike the Recommendation Engine, which determines what learning activities should be performed, the Learning Path Engine determines the most appropriate order in which those activities should occur.

The engine considers learner ability, concept mastery, prerequisite relationships, curriculum structure, and educational objectives to construct adaptive learning pathways that maximize learning efficiency.

---

# 2. Objectives

The Learning Path Engine aims to:

- Generate personalized learning paths.
- Respect prerequisite relationships.
- Adapt learning sequences to learner progress.
- Optimize educational progression.
- Prevent learners from skipping foundational concepts.
- Support individualized learning experiences.
- Supply ordered learning activities to the Adaptive Decision Engine.

---

# 3. Purpose within CogniLearn AI

The Learning Path Engine answers the following question:

> **"In what sequence should this learner study the recommended topics?"**

Rather than presenting recommendations independently, the engine organizes them into a coherent educational pathway.

---

# 4. Position within the Educational Intelligence Pipeline

```
Mastery Engine

      │

      ▼

Recommendation Engine

      │

      ▼

Learning Path Engine

      │

Personalized Learning Path

      │

      ▼

Adaptive Decision Engine
```

The Learning Path Engine converts recommendations into an ordered educational journey.

---

# 5. Inputs

The Learning Path Engine receives:

| Input | Description |
|--------|-------------|
| Learner Ability | Overall learner ability (θ) |
| Mastery Profile | Current topic mastery |
| Recommendation List | Generated learning recommendations |
| Curriculum Structure | Course organization |
| Topic Dependencies | Prerequisite relationships |
| Learning Outcomes | Educational objectives |

---

# 6. Outputs

The engine produces:

| Output | Description |
|---------|-------------|
| Personalized Learning Path | Ordered learning activities |
| Next Learning Activity | Immediate recommended activity |
| Future Learning Sequence | Planned progression |
| Learning Milestones | Intermediate educational goals |

---

# 7. Learning Path Strategy

The Learning Path Engine constructs learning paths using educational evidence.

The engine considers:

- Topic prerequisites
- Mastery levels
- Learner ability
- Curriculum order
- Learning outcomes
- Recommendation priority
- Assessment history

The resulting path is individualized for every learner.

---

# 8. Learning Path Principles

The engine follows several educational principles.

### Prerequisite First

Foundational concepts should be mastered before advanced topics.

---

### Progressive Difficulty

Difficulty increases gradually as learner ability improves.

---

### Mastery Before Progression

Learners should demonstrate sufficient mastery before advancing.

---

### Continuous Adaptation

Learning paths are recalculated whenever new assessment evidence becomes available.

---

### Personalization

Different learners may receive different learning paths even within the same course.

---

# 9. Learning Path Workflow

```
Retrieve Recommendations

        │

        ▼

Retrieve Mastery Profile

        │

        ▼

Analyze Topic Dependencies

        │

        ▼

Validate Prerequisites

        │

        ▼

Order Learning Activities

        │

        ▼

Generate Learning Path

        │

        ▼

Store Learning Path

        │

        ▼

Forward to Adaptive Decision Engine
```

---

# 10. Processing Steps

The Learning Path Engine performs the following sequence:

1. Retrieve personalized recommendations.
2. Retrieve learner mastery profile.
3. Analyze prerequisite relationships.
4. Remove invalid progression options.
5. Rank candidate learning activities.
6. Construct personalized learning sequence.
7. Store learning path.
8. Forward learning path to the Adaptive Decision Engine.

---

# 11. Learning Path Components

Each personalized learning path consists of:

- Current learning activity
- Next recommended topic
- Revision activities
- Practice assessments
- AI-supported explanations
- Learning milestones
- Future learning objectives

Together, these components form a structured educational roadmap.

---

# 12. Example Learning Path

```
Programming Fundamentals

        │

        ▼

Variables and Data Types

        │

        ▼

Control Structures

        │

        ▼

Functions

        │

        ▼

Object-Oriented Programming

        │

        ▼

Practice Assessment

        │

        ▼

AI Tutor Explanation

        │

        ▼

Advanced Programming Concepts
```

Different learners may follow different paths depending on their mastery and performance.

---

# 13. Integration with Other Components

### Receives Data From

- Recommendation Engine
- Mastery Engine
- Course Service
- Learner Service

### Sends Data To

- Adaptive Decision Engine
- Teaching Engine

---

# 14. Data Flow

```
Recommendation Engine

      │

      ▼

Learning Path Engine

      │

      ▼

Learning Path Repository

      │

      ▼

Adaptive Decision Engine
```

---

# 15. Pseudocode

```text
Retrieve recommendation list

Retrieve learner mastery

Analyze curriculum structure

Validate prerequisites

Rank activities

Generate learning sequence

Store learning path

Return personalized learning path
```

---

# 16. Performance Considerations

The Learning Path Engine should:

- Generate learning paths in real time.
- Support large curricula.
- Recalculate paths efficiently.
- Minimize unnecessary path changes.
- Scale across many concurrent learners.

---

# 17. Advantages

The Learning Path Engine provides:

- Personalized educational sequencing.
- Efficient learning progression.
- Respect for prerequisite relationships.
- Adaptive curriculum navigation.
- Improved learner engagement.
- Better educational outcomes.
- Explainable learning pathways.

---

# 18. Limitations

Current implementation limitations include:

- Depends on predefined curriculum structures.
- Assumes prerequisite relationships are accurate.
- Does not consider learner scheduling preferences.
- Uses rule-based sequencing.

Future versions may include:

- Reinforcement learning for path optimization.
- Dynamic prerequisite discovery.
- Competency-based progression.
- Multi-objective optimization.
- Time-aware learning plans.

---

# 19. Future Enhancements

Potential enhancements include:

- Personalized study schedules.
- Adaptive pacing.
- Calendar integration.
- Goal-based pathway optimization.
- Collaborative learning paths.
- AI-assisted curriculum planning.
- Predictive learning trajectory analysis.

---

# 20. Relationship with Previous Algorithms

| Algorithm | Responsibility |
|-----------|----------------|
| IRT Engine | Estimate learner ability |
| BKT Engine | Estimate concept mastery |
| Mastery Engine | Build learner mastery profile |
| Recommendation Engine | Identify appropriate learning activities |
| Learning Path Engine | Organize learning activities into an optimal sequence |

The Learning Path Engine transforms recommendations into structured educational journeys tailored to each learner.

---

# 21. Summary

The Learning Path Engine generates personalized learning sequences that guide learners through educational content in an effective and pedagogically appropriate order. By combining learner ability, mastery information, recommendations, curriculum structure, and prerequisite relationships, the engine creates adaptive learning pathways that evolve with learner progress.

These personalized learning paths provide the Adaptive Decision Engine with an ordered educational plan, ensuring that every instructional decision aligns with the learner's current needs and long-term learning objectives.

---

# Guiding Principles

> Learning should follow a logical educational progression.

> Foundational concepts should precede advanced topics.

> Learning paths should adapt continuously to learner progress.

> Educational sequencing should be personalized rather than fixed.

> Every learning path should be explainable and evidence-based.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**


Assessment Responses
        │
        ▼
┌──────────────────────────────┐
│ Item Response Theory (IRT)   │
│ Estimate Ability (θ)         │
└──────────────────────────────┘
        │
        ▼
┌──────────────────────────────┐
│ Bayesian Knowledge Tracing   │
│ Estimate Concept Mastery     │
└──────────────────────────────┘
        │
        ▼
┌──────────────────────────────┐
│ Mastery Engine               │
│ Build Learner Profile        │
└──────────────────────────────┘
        │
        ▼
┌──────────────────────────────┐
│ Recommendation Engine        │
│ Decide What to Learn         │
└──────────────────────────────┘
        │
        ▼
┌──────────────────────────────┐
│ Learning Path Engine         │
│ Decide Learning Sequence     │
└──────────────────────────────┘
        │
        ▼
Adaptive Decision Engine
        │
        ▼
Teaching Engine
        │
        ▼
AI Service Layer
        │
        ▼
Gemini / OpenAI / Claude / Llama