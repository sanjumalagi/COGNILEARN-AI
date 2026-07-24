# Learner Model Design
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Learner Model Design |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the digital representation of a learner used by the Educational Intelligence layer for personalized, adaptive, and explainable learning. |

---

# 1. Introduction

The Learner Model is the central data model of CogniLearn AI. It represents the current educational state of each learner by maintaining information about learner ability, concept mastery, assessment history, learning progress, recommendations, and instructional preferences.

Rather than viewing a learner as simply a collection of assessment scores, CogniLearn AI maintains a continuously evolving learner profile that supports adaptive educational decision-making.

The Learner Model acts as the knowledge base for every Educational Intelligence algorithm within the platform.

---

# 2. Objectives

The Learner Model aims to:

- Represent the learner's current knowledge.
- Track learning progress over time.
- Store learner ability estimates.
- Maintain concept mastery information.
- Support adaptive assessments.
- Enable personalized recommendations.
- Guide instructional strategies.
- Continuously evolve with learner interactions.

---

# 3. Role within CogniLearn AI

The Learner Model answers the following question:

> **"What does the system currently know about this learner?"**

It serves as the single source of truth for all adaptive learning decisions.

---

# 4. Position within the Educational Intelligence Pipeline

```
Assessment Responses

        │

        ▼

IRT Engine

        │

        ▼

BKT Engine

        │

        ▼

Learner Model

        │

        ▼

Mastery Engine

        │

        ▼

Recommendation Engine

        │

        ▼

Learning Path Engine

        │

        ▼

Adaptive Decision Engine

        │

        ▼

Teaching Engine
```

The Learner Model continuously evolves as new assessment evidence becomes available.

---

# 5. Core Components

The Learner Model consists of the following components.

| Component | Purpose |
|-----------|---------|
| Learner Identity | Unique learner information |
| Ability Profile | Overall ability estimate (θ) |
| Topic Mastery | Mastery for each concept |
| Assessment History | Previous assessments |
| Learning Progress | Educational progression |
| Recommendation History | Previous recommendations |
| Learning Path Status | Current adaptive sequence |
| Teaching History | Previous instructional interactions |
| AI Interaction History | AI-assisted learning sessions |

---

# 6. Learner Identity

Basic learner information includes:

- Student ID
- Name
- Enrollment information
- Course
- Semester
- Registration date

Identity information is separated from educational intelligence to improve modularity and security.

---

# 7. Ability Profile

The Ability Profile stores the learner's overall ability estimated by the Item Response Theory (IRT) engine.

Example fields:

| Attribute | Description |
|-----------|-------------|
| Theta (θ) | Estimated learner ability |
| Confidence Score | Reliability of estimate |
| Last Updated | Timestamp |

The Ability Profile is updated after each completed assessment.

---

# 8. Topic Mastery

Concept mastery is maintained for every topic within the curriculum.

Example:

| Topic | Mastery |
|-------|----------|
| Arrays | 0.91 |
| Linked Lists | 0.76 |
| Trees | 0.48 |
| Graphs | 0.33 |

Mastery values are estimated using Bayesian Knowledge Tracing (BKT).

---

# 9. Assessment History

The learner model records:

- Completed assessments
- Questions attempted
- Correct responses
- Incorrect responses
- Response times
- Assessment dates

This historical information supports learner modeling and progress analysis.

---

# 10. Learning Progress

Learning progress includes:

- Topics completed
- Current topic
- Topics in progress
- Learning objectives achieved
- Overall completion percentage

Progress information enables adaptive curriculum navigation.

---

# 11. Recommendation History

The learner model stores previously generated recommendations.

Examples include:

- Revision recommendations
- Practice recommendations
- Advanced learning suggestions
- AI explanation requests

Maintaining recommendation history prevents repetitive instructional guidance.

---

# 12. Learning Path Status

The Learning Path component records:

- Current position
- Completed topics
- Pending topics
- Locked topics
- Next recommended topic

This enables personalized sequencing throughout the curriculum.

---

# 13. Teaching History

The learner model stores previous instructional support.

Examples include:

- AI explanations
- Worked examples
- Hints
- Revision summaries
- Practice sessions

Teaching history enables the system to avoid redundant instruction.

---

# 14. AI Interaction History

The learner model records AI-assisted learning sessions.

Stored information includes:

- AI provider
- Prompt identifier
- Teaching strategy
- Response timestamp
- Session outcome

This history supports analytics and future personalization.

---

# 15. Learner Model Structure

```
Learner Model

│

├── Identity

├── Ability Profile

├── Topic Mastery

├── Assessment History

├── Learning Progress

├── Recommendation History

├── Learning Path Status

├── Teaching History

└── AI Interaction History
```

Each component contributes to a comprehensive representation of learner knowledge and progress.

---

# 16. Data Flow

```
Assessment Response

        │

        ▼

IRT Engine

        │

        ▼

BKT Engine

        │

        ▼

Update Learner Model

        │

        ▼

Mastery Engine

        │

        ▼

Recommendation Engine
```

The learner model is continuously refined as new educational evidence is collected.

---

# 17. Relationship with Educational Intelligence

| Component | Uses Learner Model For |
|-----------|------------------------|
| IRT Engine | Ability estimation |
| BKT Engine | Mastery estimation |
| Mastery Engine | Learner profiling |
| Recommendation Engine | Personalized recommendations |
| Learning Path Engine | Adaptive sequencing |
| Adaptive Decision Engine | Educational decision-making |
| Teaching Engine | Personalized instruction |

Every Educational Intelligence component either updates or consumes the Learner Model.

---

# 18. Design Characteristics

The Learner Model is:

### Dynamic

Continuously updated with new learner evidence.

---

### Personalized

Unique to every learner.

---

### Explainable

All learner attributes originate from measurable educational evidence.

---

### Modular

Each learner component can evolve independently.

---

### Extensible

Future learner characteristics can be incorporated without redesign.

---

# 19. Future Enhancements

Future versions may include:

- Learning style preferences
- Motivation indicators
- Engagement metrics
- Emotion-aware learning signals
- Collaboration history
- Gamification achievements
- Cognitive diagnostic profiles
- Long-term learning analytics

---

# 20. Summary

The Learner Model is the central representation of learner knowledge within CogniLearn AI. It integrates learner identity, ability estimation, concept mastery, assessment history, progress tracking, recommendations, learning paths, teaching interactions, and AI-assisted learning into a unified educational profile.

By continuously evolving with learner interactions, the Learner Model enables every Educational Intelligence component to deliver personalized, adaptive, and explainable learning experiences.

---

# Guiding Principles

> The learner model should evolve continuously with educational evidence.

> Every adaptive decision should be derived from the learner model.

> Learner data should be accurate, explainable, and personalized.

> The learner model should remain modular and extensible.

> Educational Intelligence depends on an accurate representation of learner knowledge.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**