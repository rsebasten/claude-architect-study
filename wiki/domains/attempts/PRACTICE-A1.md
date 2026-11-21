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
| 5 | `PRACTICE-Q05` | 5 | 2211 | D | D | Correct |
| 6 | `PRACTICE-Q06` | 6 | 2226 | B | A | Incorrect |
| 7 | `PRACTICE-Q07` | 7 | 2241 | B | B | Correct |
| 8 | `PRACTICE-Q08` | 8 | 2256 | D | A | Incorrect |
| 9 | `PRACTICE-Q09` | 9 | 2271 | A | A | Correct |

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

### Question 5 — Feedback

**Source explanation (Why D):** Coverage annotations implement graceful degradation with transparency, preserving value from completed work while propagating uncertainty to enable informed decisions about confidence.

- Answer submitted: D
- Result: Correct

### Question 6 — Feedback

**Source explanation (Why A):** Returning an error with context to the coordinator is the most effective approach because it lets the coordinator make an informed decision—skip the file, try an alternative parsing method, or notify the user—while maintaining visibility into the failure.

- Answer submitted: B
- Correct answer: A
- Result: Incorrect

### Question 7 — Feedback

**Source explanation (Why B):** Renaming the web-search tool to `extract_web_results` and updating its description to explicitly reference web search and URLs directly removes the root cause by eliminating semantic overlap between the two tool names and descriptions. This makes each tool’s purpose unambiguous, enabling the coordinator to reliably distinguish document analysis from web search.

- Answer submitted: B
- Result: Correct

### Question 8 — Feedback

**Source explanation (Why A):** The coordinator pattern provides centralized visibility into all interactions, uniform error handling across the system, and fine-grained control over what information each subagent receives—these are the primary advantages of a star-shaped communication topology.

- Answer submitted: D
- Correct answer: A
- Result: Incorrect

### Question 9 — Feedback

**Source explanation (Why A):** Returning structured error context—including failure type, executed query, partial results, and alternative approaches—gives the coordinator everything needed to make intelligent recovery decisions (e.g., retry with a modified query or continue with partial results). It preserves maximum context for informed coordination-level decision-making.

- Answer submitted: A
- Result: Correct
