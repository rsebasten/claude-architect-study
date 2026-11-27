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
| 10 | `PRACTICE-Q10` | 10 | 2286 | D | A | Incorrect |
| 11 | `PRACTICE-Q11` | 11 | 2301 | D | B | Incorrect |
| 12 | `PRACTICE-Q12` | 12 | 2316 | C | D | Incorrect |
| 13 | `PRACTICE-Q13` | 13 | 2331 | C | C | Correct |
| 14 | `PRACTICE-Q14` | 14 | 2346 | A | A | Correct |
| 15 | `PRACTICE-Q15` | 15 | 2361 | B | D | Incorrect |

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

### Question 11 — Feedback

**Source explanation (Why B):** Having the coordinator explicitly partition the research space before delegating is most effective because it addresses the root cause—unclear task boundaries—before any work begins. It preserves parallelism while preventing duplicated effort and wasted tokens.

- Answer submitted: D
- Correct answer: B
- Result: Incorrect

### Question 10 — Feedback

**Source explanation (Why A):** Replacing a general-purpose tool with a document-specific tool that validates URLs against document formats fixes the root cause by constraining capability at the interface level. This follows the principle of least privilege, making undesired search behavior impossible rather than merely discouraged.

- Answer submitted: D
- Correct answer: A
- Result: Incorrect

### Question 12 — Feedback

**Source explanation (Why D):** A timeout (access failure) and “0 results” (valid empty result) are semantically different outcomes requiring different responses. Distinguishing them allows the coordinator to retry the patent database while accepting the industry reports “0 results” as a valid, informative finding.

- Answer submitted: C
- Correct answer: D
- Result: Incorrect

### Question 13 — Feedback

**Source explanation (Why C):** Putting a key-findings summary at the start leverages primacy effects so critical information sits in the most reliably processed position. Adding explicit section headings throughout helps the model navigate and attend to mid-input content, directly mitigating the “lost in the middle” phenomenon.

- Answer submitted: C
- Result: Correct

### Question 14 — Feedback

**Source explanation (Why A):** Modifying upstream agents to return structured data fixes the root cause by reducing token volume at the source while preserving essential information. It avoids passing bulky page content and reasoning traces that inflate tokens without improving the synthesis step.

- Answer submitted: A
- Result: Correct

### Question 15 — Feedback

**Source explanation (Why D):** A limited-scope fact-verification tool lets the synthesis agent handle 85% of simple checks directly, eliminating most loops, while preserving the coordinator delegation path for the 15% of complex verifications. This applies least privilege while significantly reducing latency.

- Answer submitted: B
- Correct answer: D
- Result: Incorrect

### Question 16 — Feedback

**Source explanation (Why B):** Using `--output-format json` with `--json-schema` enforces structured output at the CLI level, guaranteeing well-formed JSON with the required fields (file path, line number, severity, suggested fix) that can be reliably parsed and posted as inline PR comments via the GitHub API. It leverages built-in CLI capabilities designed specifically for structured output.

- Answer submitted: B
- Result: Correct

### Question 17 — Feedback

**Source explanation (Why A):** A second independent Claude Code instance without access to the generator’s reasoning directly addresses the root cause by avoiding confirmation bias. This “fresh eyes” perspective mirrors human peer review, where another reviewer catches issues the author rationalized.

- Answer submitted: A
- Result: Correct

### Question 18 — Feedback

**Source explanation (Why B):** A “fire-and-forget” asynchronous Batch API model has no mechanism to intercept a tool call during a request, execute the tool, and return results for Claude to continue analysis. This is fundamentally incompatible with iterative tool-calling workflows that require multiple tool request/response rounds within a single logical interaction.

- Answer submitted: D
- Correct answer: B
- Result: Incorrect

### Question 19 — Feedback

**Source explanation (Why B):** PR style checks block developers and require immediate responses via synchronous calls, while weekly security audits and nightly test generation are scheduled tasks with flexible deadlines that can tolerate up to a 24-hour batch window—capturing 50% savings for both.

- Answer submitted: B
- Result: Correct

### Question 20 — Feedback

**Source explanation (Why D):** Few-shot examples are the most effective technique for achieving consistent output format when instructions alone produce variable results. Providing 3–4 examples that show the exact desired structure (issue, location, concrete fix) gives the model a concrete pattern to follow, which is more reliable than abstract instructions.

- Answer submitted: D
- Result: Correct

### Question 21 — Feedback

**Source explanation (Why B):** Deep analysis is an ideal candidate for batch processing because it already runs overnight, tolerates delay, and uses a polling model before publishing results—matching the asynchronous, polling-based architecture of the Message Batches API while capturing 50% savings.

- Answer submitted: B
- Result: Correct

### Question 22 — Feedback

**Source explanation (Why D):** Explicit criteria—flagging comments only when claimed behavior contradicts actual code behavior—directly addresses the root cause by replacing a vague instruction with a precise definition of what constitutes a problem. This reduces false positives on acceptable patterns and misses of truly misleading comments.

- Answer submitted: D
- Result: Correct

### Question 23 — Feedback

**Source explanation (Why A):** Temporarily disabling high-false-positive categories immediately stops trust erosion by removing noisy findings that cause developers to dismiss everything, while preserving value from high-precision categories like security and correctness. It also creates space to improve prompts for problematic categories before re-enabling them.

- Answer submitted: B
- Correct answer: A
- Result: Incorrect

### Question 24 — Feedback

**Source explanation (Why A):** Including the existing test file fixes the root cause of duplication: Claude can only avoid suggesting already-covered scenarios if it knows what tests already exist. This gives Claude the information needed to propose genuinely new, valuable tests.

- Answer submitted: A
- Result: Correct

### Question 25 — Feedback

**Source explanation (Why D):** Including prior review findings in context lets Claude distinguish new problems from those already addressed in recent commits. This preserves review thoroughness while using Claude’s reasoning to avoid redundant feedback on fixed code.

- Answer submitted: D
- Result: Correct

### Question 26 — Feedback

**Source explanation (Why B):** The `-p` (or `--print`) flag is the documented way to run Claude Code non-interactively. It processes the prompt, prints the result to stdout, and exits without waiting for user input—ideal for CI/CD pipelines.

- Answer submitted: B
- Result: Correct

### Question 27 — Feedback

**Source explanation (Why B):** Focused per-file passes address the root cause—attention dilution—by ensuring consistent depth and reliable local issue detection. A separate integration-oriented pass then covers cross-file concerns such as dependency and data-flow interactions.

- Answer submitted: B
- Result: Correct

### Question 28 — Feedback

**Source explanation (Why A):** Including rationale and confidence directly in each finding reduces investigation time by letting developers quickly triage without opening each finding. It satisfies the “no filtering” constraint because all findings remain visible while accelerating developer decision-making.

- Answer submitted: C
- Correct answer: A
- Result: Incorrect

### Question 29 — Feedback

**Source explanation (Why A):** Temporarily disabling high-false-positive categories immediately stops trust erosion by removing noisy findings that cause developers to dismiss everything, while preserving value from high-precision categories like security and correctness. It also creates space to improve prompts for problematic categories before re-enabling them.

- Answer submitted: C
- Correct answer: A
- Result: Incorrect

### Question 30 — Feedback

**Source explanation (Why C):** Message Batches API processing can take up to 24 hours with no latency SLA, which is acceptable for overnight technical debt reports but unacceptable for blocking pre-merge checks where developers wait. This matches each workflow to the right API based on latency requirements.

- Answer submitted: C
- Result: Correct

### Question 31 — Feedback

**Source explanation (Why B):** Concrete input-output examples remove ambiguity inherent in prose descriptions by showing Claude the exact expected transformation results. This directly addresses the root cause—misinterpretation of textual requirements—by providing unambiguous patterns for field nesting and timestamp formatting.

- Answer submitted: A
- Correct answer: B
- Result: Incorrect

### Question 32 — Feedback

**Source explanation (Why B):** Slack integration has multiple valid approaches with significantly different architectural implications, and requirements are ambiguous. Planning mode lets you evaluate trade-offs among webhooks, bot tokens, and Slack Apps and align on an approach before implementation.

- Answer submitted: B
- Result: Correct

### Question 33 — Feedback

**Source explanation (Why D):** CLAUDE.md content loads in every session, ensuring coding standards and testing conventions always apply, while Skills are invoked on demand when Claude detects trigger keywords—ideal for workflow-specific guidance like PR review, deployment, and migrations.

- Answer submitted: B
- Correct answer: D
- Result: Incorrect

### Question 34 — Feedback

**Source explanation (Why A):** Planning mode is the right strategy for complex architectural restructuring like splitting a monolith: it allows safe exploration and informed decisions about boundaries before committing to potentially expensive changes across many files.

- Answer submitted: A
- Result: Correct

### Question 35 — Feedback

**Source explanation (Why A):** `context: fork` runs the analysis in an isolated subagent context so the large output does not pollute the main session’s context window and Claude does not lose track of the original task. It preserves full analysis capability while keeping the main session responsive.

- Answer submitted: A
- Result: Correct

### Question 36 — Feedback

**Source explanation (Why C):** Skill resolution is positional: enterprise overrides personal, and personal overrides project. A personal skill at `~/.claude/skills/commit/SKILL.md` therefore shadows the team's `.claude/skills/commit/SKILL.md` for that developer alone — nothing in the repository changes, so teammates keep running the project version and `/commit` behaves the same for everyone else. A works mechanically but is the weaker recommendation: the project `/commit` stays active alongside `/my-commit`, and two skills with near-identical `description` fields make Claude's automatic skill selection unpredictable, while breaking the muscle memory and team docs that say to run `/commit`. B fails because skill frontmatter has no conditional or username facility, and it would require editing the shared project file the scenario rules out. D fails because there is no `override` field — precedence comes from location, not from a declaration.

- Answer submitted: C
- Result: Correct

### Question 37 — Feedback

**Source explanation (Why A):** If the guidance was added only to the original developers’ user-level configs and not to the project-level `.claude/CLAUDE.md`, new team members won’t receive it. Moving it to the project-level configuration ensures all current and future team members automatically get the guidance.

- Answer submitted: B
- Correct answer: A
- Result: Incorrect

### Question 38 — Feedback

**Source explanation (Why D):** A skill invoked on demand loads the example context only when generating new endpoints, not during unrelated tasks like debugging or review. This keeps the main context clean while preserving high-quality generation when needed.

- Answer submitted: A
- Correct answer: D
- Result: Incorrect
