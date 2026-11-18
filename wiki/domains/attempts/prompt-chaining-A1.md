# Attempt A1 — Prompt Chaining

- Source: [Guide §6.3 Prompt Chaining](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md#63-prompt-chaining)
- Started: 2026-11-18
- Status: in progress
- Questions: 7
- Submitted: 1
- First-attempt score: 1/1
- Checkpoint: Question 2

## Responses

### Question 1 — Sequential focused passes
- Selected answer: **B** — Run a focused local-issue analysis on each file, then run a separate integration pass across the files.
- Result: **Correct**
- First attempt: Yes
- Explanation: Prompt chaining decomposes a predictable multi-aspect review into sequential focused steps. Analyze each file for local issues, then perform a separate cross-file integration pass for module-boundary problems. This reduces attention dilution, improves consistency per file, and checks interactions between files.
- Remediation / escalation: No remediation escalation required. Reinforce the two-layer review model: local findings first; cross-file integration findings second.
- Weakness observed: None from this response.

## Weaknesses

No weaknesses identified yet. Update this section after each incorrect answer or request for deeper explanation.
