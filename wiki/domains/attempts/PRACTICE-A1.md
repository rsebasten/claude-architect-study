# Source Quiz Attempt — PRACTICE-A1

- **Source ID:** `SRC-CCA-GUIDE`
- **Source:** [Claude Certified Architect Guide](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md)
- **Cached verbatim archive:** [claude-certified-architect-guide_en-questions.md](../claude-certified-architect-guide_en-questions.md)
- **Source revision:** `cf335d1fd965e8e763deb0714ffe743697aa0a58`
- **Attempt type:** Practice Test
- **Status:** In progress

## Answers

| Attempt question | Stable source ID | Original source question | Source line | Selected answer | Correct answer | Result |
|---:|---|---:|---:|---|---|
| 1 | `PRACTICE-Q01` | 1 | 2151 | D | D | Correct |
| 2 | `PRACTICE-Q02` | 2 | 2166 | C | C | Correct |
| 3 | `PRACTICE-Q03` | 3 | 2181 | D | D | Correct |
| 4 | `PRACTICE-Q04` | 4 | 2196 | C | C | Correct |

### Question 1 — Feedback

**Source explanation (Why D):** This approach preserves separation of responsibilities: the analysis agent completes its core work without blocking, preserves both conflicting values with clear attribution, and correctly passes reconciliation to the coordinator, which has broader context.

- Answer submitted: D
- Result: Correct

### Question 2 — Feedback

**Source explanation (Why C):** In a coordinator–subagent architecture, the coordinator forwards both result sets to the synthesis agent for centralized integration, preserving control and ensuring high-quality merging.

- Answer submitted: C
- Result: Correct

### Question 3 — Feedback

**Source explanation (Why D):** Handle errors at the lowest level capable of resolving them. Local recovery reduces coordinator workload while still escalating truly unrecoverable issues with full context and partial progress.

- Answer submitted: D
- Result: Correct

### Question 4 — Feedback

**Source explanation (Why C):** The coordinator decomposed a broad topic only into visual-art subtasks, missing music, literature, and film entirely. Since subagents executed their assignments correctly, the narrow decomposition is the obvious root cause.

- Answer submitted: C
- Result: Correct
