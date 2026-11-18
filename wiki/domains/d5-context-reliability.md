---
domain: [D5]
sources: [exam-guide, code, runs]
updated: 2026-11-17
---
# D5 Context Management & Reliability

**Weight:** 15% [exam-guide p.3]

## Task statements

| # | Task statement | Key facts to know | Source |
|---|---|---|---|
| 5.1 | Preserve critical info in long interactions | Progressive summaries blur numbers, %, dates and customer expectations, so keep a persistent **"case facts" block** outside the summarised history. **"Lost in the middle"**: put key summaries at the **start** and use section headers. Trim verbose tool output to the relevant fields (5 of 40+). Send the full history in each request. Upstream agents return structured facts, citations and dates, not verbose reasoning. | [exam-guide p.19–20] |
| 5.2 | Escalation and ambiguity | Escalate when the customer **asks for a human (immediately, no investigation first)**, when policy is silent or ambiguous (competitor price match), or when no progress is possible. Frustrated but solvable: acknowledge and offer to resolve, escalate if they insist. **Sentiment and self-reported confidence are unreliable** triggers. Multiple customer matches: **ask for another identifier**, don't guess. Give explicit escalation criteria with few-shot examples. | [exam-guide p.20–21] |
| 5.3 | Error propagation across agents | Structured error context: **failure type, what was attempted, partial results, alternatives**. Access failure ≠ valid empty result. Generic "search unavailable" hides context. Anti-patterns: **silently suppressing** errors (empty = success) **and** killing the whole workflow on one failure. Subagents recover locally from transient errors. Synthesis carries **coverage annotations** (well supported vs gaps). | [exam-guide p.21] |
| 5.4 | Context in large codebase exploration | Long sessions degrade: inconsistent answers, "typical patterns" instead of the specific classes found. Use **scratchpad files** for findings. Subagents isolate verbose exploration. Summarise a phase before spawning the next phase's subagents. Crash recovery: each agent exports state; the coordinator loads a **manifest** on resume. **`/compact`** frees context. | [exam-guide p.21–22] |
| 5.5 | Human review and confidence calibration | A 97% overall score can hide poor doc types or fields, so measure **by document type and field**. **Stratified random sampling** of high-confidence output. Field-level confidence **calibrated on labelled validation sets**. Route low-confidence or contradictory docs to humans. | [exam-guide p.22] |
| 5.6 | Provenance in multi-source synthesis | Summarising drops attribution, so keep **structured claim-source mappings** (URL, doc name, excerpt) through synthesis. **Conflicting stats: annotate both with sources, don't pick one.** Require **publication or collection dates** so time differences aren't mistaken for contradictions. Separate **well-established vs contested** sections. Render by type: financial data as tables, news as prose, technical findings as lists. | [exam-guide p.23] |

## Common traps

| Wrong answer pattern | Why it's wrong | Source |
|---|---|---|
| Investigate first when the customer asks for a human | Honour the request immediately | [exam-guide p.21] |
| Escalate based on sentiment or the model's confidence score | Unreliable proxies for complexity | [exam-guide p.20] |
| Pick the most likely of several customer matches | Ask for another identifier | [exam-guide p.20–21] |
| Return empty results as success on a subagent timeout | Hides the failure from the coordinator | [exam-guide p.21, p.31] |
| Abort the whole pipeline on one subagent failure | Continue with partial results and annotate the gaps | [exam-guide p.21] |
| Average or choose one of two conflicting statistics | Keep both, with attribution | [exam-guide p.23] |
| Trust 97% aggregate accuracy to cut human review | Check by segment first | [exam-guide p.22] |

## Seen in my code

| What | Where |
|---|---|
| `--timeout`: structured timeout error → `status: partial` → the coordinator continues and the gap appears in Coverage gaps (5.3) | `research/research_agent.py`, [runs ex4-timeout.log] |
| Claim/quote/URL/date contract; Established vs Contested; 41% vs 34% and $18 vs $21 both kept (5.6) | `research/research_agent.py`, `research/corpus.py` |
| Code check that every report URL traces back to a finding (5.6) | `research/research_agent.py` `check()` |
| The synthesiser judged source independence (the Gazette's 41% repeats council data) (5.6) | [runs ex4-parallel.log] |
| Accuracy by doc type and field, confidence routing (5.5) | `extraction/pipeline.py` `report()` / `route()` |
| Escalation ticket when the agent can't finish (5.2) | `support_agent/escalation_agent.py` |

## Related
[D1](d1-agent-architecture.md) (coordinator, sessions) · [D4](d4-prompt-structured-output.md) (validation, review)
