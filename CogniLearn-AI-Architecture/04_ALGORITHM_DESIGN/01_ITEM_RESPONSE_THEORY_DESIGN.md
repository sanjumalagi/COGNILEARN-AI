# Item Response Theory (IRT) Design
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Item Response Theory (IRT) Design |
| Version | 1.0 |
| Status | Approved Design Document |
| Purpose | Define the design and implementation of the Item Response Theory (IRT) engine used to estimate learner ability and support adaptive educational decisions within CogniLearn AI. |

---

# 1. Introduction

Item Response Theory (IRT) is a statistical framework used to estimate a learner's ability based on their responses to assessment items. Unlike traditional scoring methods that simply count the number of correct answers, IRT evaluates learner performance by considering both the learner's ability and the characteristics of each assessment item.

Within CogniLearn AI, IRT serves as the primary mechanism for estimating learner ability (θ). This estimate is later combined with Bayesian Knowledge Tracing (BKT) to produce adaptive educational decisions.

The IRT Engine operates within the Educational Intelligence layer and provides evidence-based learner modeling before AI-assisted teaching begins.

---

# 2. Objectives

The IRT Engine aims to:

- Estimate learner ability (θ).
- Measure learner progress over time.
- Support adaptive difficulty selection.
- Identify learners requiring additional support.
- Provide ability estimates for recommendation generation.
- Improve personalization of learning activities.
- Supply educational evidence to the Adaptive Decision Engine.

---

# 3. Purpose within CogniLearn AI

The IRT Engine is responsible for answering the following question:

> **"How capable is this learner based on assessment evidence?"**

Its output does not directly generate educational content.

Instead, it supplies an ability estimate that guides:

- Learning path generation
- Difficulty adaptation
- Recommendation generation
- Teaching context preparation

---

# 4. Position within the Educational Intelligence Pipeline

```
Assessment Responses

        │

        ▼

IRT Engine

        │

Ability Estimate (θ)

        │

        ▼

BKT Engine

        │

Mastery Analysis

        │

        ▼

Adaptive Decision Engine
```

The IRT Engine executes immediately after assessment evaluation.

---

# 5. Inputs

The IRT Engine receives the following information.

| Input | Description |
|--------|-------------|
| Student ID | Learner identifier |
| Assessment Responses | Correct and incorrect answers |
| Question Difficulty | Difficulty value assigned to each assessment item |
| Assessment Metadata | Topic, Learning Outcome, Assessment ID |
| Historical Ability | Previous θ estimate (optional) |

---

# 6. Outputs

The engine produces the following outputs.

| Output | Description |
|---------|-------------|
| Ability (θ) | Estimated learner ability |
| Ability Category | Beginner, Intermediate, Advanced |
| Confidence Score | Reliability of the estimate |
| Difficulty Recommendation | Suggested difficulty for future assessments |

---

# 7. IRT Model

CogniLearn AI adopts the **One-Parameter Logistic Model (1PL)**, commonly known as the **Rasch Model**, due to its simplicity, interpretability, and suitability for educational applications.

The probability of a learner answering an assessment item correctly is given by:

\[
P(\theta)=\frac{1}{1+e^{-(\theta-b)}}
\]

Where:

- **θ** = Learner ability
- **b** = Item difficulty

The model assumes that the probability of a correct response increases as learner ability exceeds item difficulty.

---

# 8. Ability Scale

Learner ability is represented using a continuous scale.

| θ Value | Interpretation |
|----------|----------------|
| θ < -1.0 | Beginner |
| -1.0 ≤ θ ≤ 1.0 | Intermediate |
| θ > 1.0 | Advanced |

These ranges are configurable and may be adjusted based on empirical evaluation.

---

# 9. Algorithm Workflow

```
Assessment Submission

        │

        ▼

Collect Responses

        │

        ▼

Retrieve Item Difficulties

        │

        ▼

Estimate Ability (θ)

        │

        ▼

Classify Ability

        │

        ▼

Store Ability

        │

        ▼

Forward to BKT Engine
```

---

# 10. Processing Steps

The IRT Engine performs the following steps:

1. Retrieve learner assessment responses.
2. Retrieve item difficulty values.
3. Estimate learner ability (θ).
4. Update learner profile.
5. Store the latest ability estimate.
6. Forward the estimate to the BKT Engine.

---

# 11. Integration with Other Components

The IRT Engine collaborates with multiple software components.

### Receives Data From

- Assessment Service
- Learner Service

### Sends Data To

- BKT Engine
- Adaptive Decision Engine
- Recommendation Engine

---

# 12. Data Flow

```
Assessment

        │

        ▼

Assessment Service

        │

        ▼

IRT Engine

        │

        ▼

Learner Profile

        │

        ▼

Adaptive Intelligence
```

---

# 13. Pseudocode

```text
Receive assessment responses

Retrieve question difficulties

Estimate learner ability (θ)

Update learner profile

Store θ value

Return ability estimate
```

---

# 14. Performance Considerations

The IRT Engine should:

- Execute quickly after assessment submission.
- Minimize computational overhead.
- Produce deterministic results.
- Scale to large numbers of learners.
- Support repeated ability updates.

---

# 15. Advantages

Using IRT provides several benefits:

- Ability estimation beyond raw scores.
- Personalized difficulty adjustment.
- Objective learner comparison.
- Evidence-based adaptation.
- Improved recommendation quality.
- Explainable learner modeling.

---

# 16. Limitations

Current implementation limitations include:

- Uses only the 1PL (Rasch) model.
- Assumes equal discrimination across items.
- Requires calibrated item difficulty values.
- Does not model guessing behavior.

Future versions may adopt:

- 2PL Model
- 3PL Model
- Multidimensional IRT

---

# 17. Future Enhancements

Potential improvements include:

- Automatic item calibration.
- Online ability estimation.
- Bayesian IRT.
- Adaptive testing integration.
- Multidimensional learner modeling.
- Real-time ability tracking.

---

# 18. Summary

The Item Response Theory (IRT) Engine provides the learner ability estimation capability within CogniLearn AI. By evaluating assessment responses in relation to item difficulty, the engine produces an evidence-based estimate of learner ability that supports adaptive educational decision-making.

The estimated ability value is subsequently combined with mastery information from the Bayesian Knowledge Tracing Engine, enabling the Adaptive Decision Engine to generate personalized learning paths, recommendations, and AI-assisted instructional support.

---

# Guiding Principles

> Ability estimation should be based on learner evidence rather than raw scores.

> IRT provides educational intelligence, not instructional content.

> Learner ability should continuously evolve with new assessment evidence.

> Ability estimates should support explainable adaptive learning decisions.

> Educational reasoning must precede AI-assisted teaching.

---

**End of Document**