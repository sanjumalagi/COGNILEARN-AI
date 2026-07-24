# Teaching Engine Design
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Teaching Engine Design |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the design and implementation of the Teaching Engine responsible for transforming educational decisions into personalized instructional contexts before invoking the AI Service Layer. |

---

# 1. Introduction

The Teaching Engine is the final component of the Educational Intelligence layer within CogniLearn AI. Its primary responsibility is to translate adaptive educational decisions into structured instructional contexts that guide AI-generated teaching.

Unlike traditional AI tutoring systems where the language model independently determines teaching strategies, the Teaching Engine ensures that instructional content is driven by educational intelligence rather than the AI model itself.

The Teaching Engine prepares complete educational context before interacting with the AI Service Layer, enabling personalized, explainable, and pedagogically appropriate instruction.

---

# 2. Objectives

The Teaching Engine aims to:

- Transform educational decisions into teaching strategies.
- Prepare personalized instructional context.
- Select appropriate teaching methods.
- Determine the level of explanation required.
- Support adaptive instruction.
- Guide AI-assisted content generation.
- Ensure educational consistency.

---

# 3. Purpose within CogniLearn AI

The Teaching Engine answers the following question:

> **"How should this learner be taught?"**

The engine determines instructional intent before any AI-generated content is requested.

Examples include:

- Provide a detailed explanation.
- Give a concise revision summary.
- Generate additional practice questions.
- Offer a worked example.
- Provide hints instead of direct answers.
- Encourage conceptual understanding.

---

# 4. Position within the Educational Intelligence Pipeline

```
Adaptive Decision Engine

        │

        ▼

Teaching Engine

        │

Teaching Context

        │

        ▼

AI Service Layer

        │

        ▼

Large Language Model
```

The Teaching Engine converts educational decisions into instructional strategies.

---

# 5. Inputs

The Teaching Engine receives:

| Input | Description |
|--------|-------------|
| Educational Decision | Selected by the Adaptive Decision Engine |
| Learner Ability | Overall learner ability |
| Mastery Profile | Current learner mastery |
| Current Topic | Topic being studied |
| Learning Objective | Educational objective to achieve |
| Recommendation | Suggested learning activity |
| Learning Path | Current learning sequence |

---

# 6. Outputs

The engine produces:

| Output | Description |
|---------|-------------|
| Teaching Context | Structured instructional information |
| Teaching Strategy | Selected instructional approach |
| AI Prompt Context | Educational data for prompt generation |
| Instruction Metadata | Difficulty, objective, learner state |

---

# 7. Teaching Strategy

The Teaching Engine selects instructional strategies according to learner needs.

Possible strategies include:

- Concept Explanation
- Guided Learning
- Step-by-Step Demonstration
- Worked Examples
- Revision Summary
- Practice-Oriented Teaching
- Hint-Based Learning
- Challenge-Based Learning

Each strategy is chosen using learner evidence rather than generic prompting.

---

# 8. Teaching Context Model

The Teaching Engine builds a structured teaching context containing:

- Current topic
- Learning objective
- Learner ability
- Mastery level
- Weak concepts
- Recommended difficulty
- Teaching strategy
- Expected learning outcome
- Assessment history

This context becomes the foundation for AI-generated instructional content.

---

# 9. Teaching Workflow

```
Receive Educational Decision

        │

        ▼

Retrieve Learner Context

        │

        ▼

Select Teaching Strategy

        │

        ▼

Build Teaching Context

        │

        ▼

Generate AI Prompt Context

        │

        ▼

Forward to AI Service Layer
```

---

# 10. Processing Steps

The Teaching Engine performs the following sequence:

1. Receive educational decision.
2. Retrieve learner information.
3. Retrieve mastery profile.
4. Identify current learning objective.
5. Select teaching strategy.
6. Build structured teaching context.
7. Generate AI prompt context.
8. Forward the instructional context to the AI Service Layer.

---

# 11. Teaching Strategies

| Learner State | Teaching Strategy |
|---------------|-------------------|
| Low mastery | Detailed explanation |
| Moderate mastery | Guided practice |
| High mastery | Advanced challenges |
| Repeated mistakes | Worked examples |
| Misconceptions | Concept clarification |
| Strong performance | Enrichment activities |

These strategies ensure that instructional support matches learner needs.

---

# 12. Teaching Context Structure

The Teaching Engine generates a structured teaching context.

Example:

```json
{
  "topic": "Binary Search",
  "learning_objective": "Understand divide-and-conquer searching",
  "learner_level": "Intermediate",
  "mastery": 0.63,
  "difficulty": "Medium",
  "teaching_strategy": "Worked Example",
  "instruction_type": "Step-by-Step Explanation",
  "weak_concepts": [
    "Loop Invariants",
    "Search Space Reduction"
  ]
}
```

This context is independent of the AI provider and represents the educational intent of the lesson.

---

# 13. Integration with Other Components

### Receives Data From

- Adaptive Decision Engine
- Learner Service
- Course Service
- Assessment Service

### Sends Data To

- AI Service Layer
- Analytics Service

---

# 14. Data Flow

```
Adaptive Decision Engine

        │

        ▼

Teaching Engine

        │

        ▼

Teaching Context Repository

        │

        ▼

AI Service Layer
```

---

# 15. Pseudocode

```text
Receive educational decision

Retrieve learner profile

Retrieve mastery information

Select teaching strategy

Build teaching context

Generate AI prompt context

Return teaching context
```

---

# 16. Performance Considerations

The Teaching Engine should:

- Generate teaching context in real time.
- Produce deterministic instructional strategies.
- Minimize latency before AI invocation.
- Support multiple AI providers.
- Scale efficiently across many learners.

---

# 17. Advantages

The Teaching Engine provides:

- Personalized instruction.
- Explainable teaching strategies.
- Consistent instructional quality.
- AI-provider independence.
- Educationally grounded prompting.
- Improved learner engagement.
- Better learning outcomes.

---

# 18. Limitations

Current implementation limitations include:

- Uses predefined instructional strategies.
- Does not evaluate learner emotions.
- Does not support multimodal teaching adaptation.
- Relies on accurate learner modeling.

Future versions may incorporate:

- Emotion-aware tutoring.
- Voice-based instruction.
- Learning style adaptation.
- Multimodal teaching.
- Reinforcement learning for instructional optimization.

---

# 19. Future Enhancements

Potential improvements include:

- Adaptive Socratic questioning.
- Interactive tutoring dialogues.
- Personalized feedback generation.
- Real-time instructional adaptation.
- Collaborative learning support.
- Explainable instructional reasoning.
- Intelligent lesson planning.

---

# 20. Relationship with Previous Algorithms

| Algorithm | Responsibility |
|-----------|----------------|
| IRT Engine | Estimate learner ability |
| BKT Engine | Estimate concept mastery |
| Mastery Engine | Build learner profile |
| Recommendation Engine | Recommend learning activities |
| Learning Path Engine | Build personalized learning sequence |
| Adaptive Decision Engine | Select next educational action |
| Teaching Engine | Convert educational decisions into instructional context |

The Teaching Engine is the bridge between Educational Intelligence and AI-powered instruction.

---

# 21. Relationship with the AI Service Layer

The Teaching Engine does **not** communicate directly with the Large Language Model.

Instead, it forwards structured instructional context to the AI Service Layer, which is responsible for:

- Prompt construction.
- AI provider selection.
- API communication.
- Response validation.
- Response parsing.
- Error handling.

This separation ensures that educational reasoning remains independent of AI implementation.

---

# 22. Summary

The Teaching Engine is the final component of the Educational Intelligence layer in CogniLearn AI. It transforms adaptive educational decisions into structured instructional contexts that guide AI-assisted teaching.

By selecting teaching strategies, preparing learner-specific context, and defining instructional intent before AI invocation, the Teaching Engine ensures that educational intelligence—not the language model—drives the teaching process. This separation enables personalized, explainable, and provider-independent instruction while maintaining a clear distinction between educational reasoning and AI-generated content.

---

# Guiding Principles

> Teaching should be guided by educational evidence.

> Instructional strategy should be selected before AI content generation.

> Educational reasoning should remain independent of AI providers.

> Teaching context should be structured, explainable, and reusable.

> AI should generate instructional content, not determine educational strategy.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**