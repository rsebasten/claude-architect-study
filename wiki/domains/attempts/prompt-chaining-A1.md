# Attempt A1 — Prompt Chaining

- Source: [Guide §6.3 Prompt Chaining](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md#63-prompt-chaining)
- Started: 2026-11-18
- Status: in progress
- Questions: 7
- Submitted: 2
- First-attempt score: 2/2
- Checkpoint: Question 3

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

## Weaknesses

No weaknesses identified from Q1–Q2. Update this section after each incorrect answer or request for deeper explanation.
