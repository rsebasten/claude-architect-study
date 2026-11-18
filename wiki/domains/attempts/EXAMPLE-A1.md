# Source Quiz Attempt — EXAMPLE-A1

- **Source ID:** `SRC-CCA-GUIDE`
- **Source:** [Claude Certified Architect Guide](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md)
- **Cached verbatim archive:** [claude-certified-architect-guide_en-questions.md](../claude-certified-architect-guide_en-questions.md)
- **Source revision:** `cf335d1fd965e8e763deb0714ffe743697aa0a58`
- **Attempt type:** Examples of Exam Questions with Explanations
- **Status:** In progress

## Answers

| Attempt question | Stable source ID | Original source question | Source line | Selected answer | Correct answer | Result |
|---:|---|---:|---:|---|---|---|
| 1 | `EXAMPLE-Q01` | 1 | 1961 | A | A | Correct |
| 2 | `EXAMPLE-Q02` | 2 | 1976 | B | B | Correct |
| 3 | `EXAMPLE-Q03` | 3 | 1991 | A | A | Correct |
| 4 | `EXAMPLE-Q04` | 4 | 2006 | A | A | Correct |
| 5 | `EXAMPLE-Q05` | 5 | 2021 | A | A | Correct |
| 6 | `EXAMPLE-Q06` | 6 | 2036 | A | A | Correct |
| 7 | `EXAMPLE-Q07` | 7 | 2051 | B | B | Correct |
| 8 | `EXAMPLE-Q08` | 8 | 2066 | A | A | Correct |
| 9 | `EXAMPLE-Q09` | 9 | 2081 | A | A | Correct |
| 10 | `EXAMPLE-Q10` | 10 | 2096 | A | A | Correct |
| 11 | `EXAMPLE-Q11` | 11 | 2111 | A | A | Correct |

### Question 1 — Feedback

**Source explanation (Why A):** When critical business logic requires a specific tool sequence, software provides **deterministic guarantees** that prompt-based approaches (B, C) cannot. D addresses availability, not tool ordering.

- Answer submitted: A
- Result: Correct

### Question 2 — Feedback

**Source explanation (Why B):** Tool descriptions are the model’s primary selection mechanism. This is the lowest-effort, highest-impact fix. A adds tokens without addressing the root cause. C is overengineering. D requires more effort than justified.

- Answer submitted: B
- Result: Correct

### Question 3 — Feedback

**Source explanation (Why A):** It directly addresses the root cause—unclear decision boundaries. B is unreliable (the model can be confidently wrong). C is overengineering. D solves a different problem (mood != complexity).

- Answer submitted: A
- Result: Correct

### Question 4 — Feedback

**Source explanation (Why A):** Project commands stored in `.claude/commands/` are version-controlled and automatically available to everyone. B is for personal commands. C is for instructions, not command definitions. D does not exist.

- Answer submitted: A
- Result: Correct

### Question 5 — Feedback

**Source explanation (Why A):** Planning mode is designed for large changes, multiple possible approaches, and architectural decisions. B risks expensive rework. C assumes you already know the structure. D is reactive.

- Answer submitted: A
- Result: Correct

### Question 6 — Feedback

**Source explanation (Why A):** `.claude/rules/` with glob patterns (e.g., `**/*.test.tsx`) enables automatic convention application based on file paths—ideal for tests spread across the codebase. B relies on model inference. C is manual/on-demand. D does not work well when relevant files are in many directories.

- Answer submitted: A
- Result: Correct

### Question 7 — Feedback

**Source explanation (Why B):** The logs show the coordinator decomposed “creative industries” only into visual subtopics, completely missing music, literature, and film. Subagents executed correctly—the issue is what they were assigned.

- Answer submitted: B
- Result: Correct

### Question 8 — Feedback

**Source explanation (Why A):** Structured error context gives the coordinator what it needs to decide whether to retry with a modified query, try an alternative approach, or continue with partial results. B hides context behind a generic status. C masks failure as success. D aborts the entire workflow unnecessarily.

- Answer submitted: A
- Result: Correct

### Question 9 — Feedback

**Source explanation (Why A):** This applies the principle of least privilege: the synthesis agent gets exactly what it needs for the 85% common case (simple fact checks) while preserving the coordinator-mediated path for complex investigations. B introduces blocking dependencies (later synthesis steps may depend on earlier verified facts). C breaks separation of responsibilities. D relies on speculative caching that cannot reliably predict needs.

- Answer submitted: A
- Result: Correct

### Question 10 — Feedback

**Source explanation (Why A):** `-p` (or `--print`) is the documented way to run Claude Code in non-interactive mode. It processes the prompt, prints to stdout, and exits. The other options are either non-existent features or Unix workarounds.

- Answer submitted: A
- Result: Correct

### Question 11 — Feedback

**Source explanation (Why A):** The Message Batches API saves 50%, but processing time can be up to 24 hours with no guaranteed latency SLA. That makes it unsuitable for blocking pre-merge checks where developers are waiting, but ideal for overnight batch workloads like tech-debt reports.

- Answer submitted: A
- Result: Correct
