# Attempt A1 — Prompt Chaining

- Source: [Guide §6.3 Prompt Chaining](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md#63-prompt-chaining)
- Started: 2026-11-18
- Status: in progress
- Questions: 7
- Submitted: 4
- First-attempt score: 4/4
- Checkpoint: Question 5

## Responses

### Question 1 — Sequential focused passes
- Selected answer: **B** — Run a focused local-issue analysis on each file, then run a separate integration pass across the files.
- Result: **Correct**
- First attempt: Yes
- Explanation: Prompt chaining decomposes a predictable multi-aspect review into sequential focused steps. Analyze each file for local issues, then perform a separate cross-file integration pass for module-boundary problems. This reduces attention dilution, improves consistency per file, and checks interactions between files.
- Remediation / escalation: No remediation escalation required. Reinforce the two-layer review model: local findings first; cross-file integration findings second.
- Weakness observed: None from this response.

### Question 2 — Attention dilution
- Selected answer: **A** — Attention dilution caused by too much material competing for model attention.
- Result: **Correct**
- First attempt: Yes
- Explanation: Prompt chaining limits the amount of material competing for attention in each step. Focused passes make it easier to analyze each file consistently instead of giving a few files deep attention while the rest receive shallow treatment. The issue is not a hard limit on reading multiple files; it is the degradation in focus when too much context is handled at once.
- Remediation / escalation: No remediation escalation required. Retain the core rationale: narrow sequential passes reduce attention dilution and improve consistency.
- Weakness observed: None from this response.

### Question 3 — Predictable repeatable workflows
- Selected answer: **B** — Prompt chaining, because the review is repeatable and its steps are known in advance.
- Result: **Correct**
- First attempt: Yes
- Explanation: Prompt chaining is well suited to predictable tasks with a stable sequence of known steps, such as a release review that follows the same checklist each time. The workflow can be decomposed into focused stages and reproduced consistently.
- Remediation / escalation: No remediation escalation required. Reinforce the selection rule: known, repeatable stages favor a predefined chain; open-ended work favors dynamic decomposition.
- Weakness observed: None from this response.

### Question 4 — Open-ended investigation
- Selected answer: **B** — Dynamic adaptive decomposition, where subtasks evolve based on intermediate findings.
- Result: **Correct**
- First attempt: Yes
- Explanation: In an unfamiliar codebase, the investigation path is not fully knowable in advance. Dynamic decomposition creates or adjusts subtasks as findings reveal new dependencies and questions. A fixed chain is better when the stages are predictable.
- Remediation / escalation: No remediation escalation required. Reinforce the decision boundary: predefined, repeatable stages favor prompt chaining; unknown scope and discovery-dependent next steps favor dynamic decomposition.
- Weakness observed: None from this response.

## Weaknesses

No weaknesses identified from Q1–Q4. Update this section after each incorrect answer or request for deeper explanation.
