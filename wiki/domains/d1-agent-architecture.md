---
domain: [D1]
sources: [exam-guide, code, runs]
updated: 2026-11-17
---
# D1 Agentic Architecture & Orchestration

**Weight:** 27%, the largest domain [exam-guide p.3]
**Scenarios:** Customer Support Resolution Agent, and others [exam-guide p.3]

## Task statements

| # | Task statement | Key facts to know | Source |
|---|---|---|---|
| 1.1 | Design agentic loops | Loop: send → check `stop_reason` → `"tool_use"`: run tools, append results, repeat; `"end_turn"`: stop. Tool results are appended to history so the model can reason about the next step. Model-driven tool choice, not a pre-set decision tree. | [exam-guide p.5] |
| 1.2 | Coordinator–subagent orchestration | Hub-and-spoke: the coordinator handles all communication, error handling and routing. Subagents have **isolated context** and don't inherit history. The coordinator picks subagents by query complexity, splits scope to avoid duplication, and can loop: check synthesis for gaps → re-delegate → re-synthesise. Risk: decomposition that's too narrow misses parts of a broad topic. | [exam-guide p.5–6] |
| 1.3 | Subagent invocation and context passing | The `Task` tool spawns subagents, and **`allowedTools` must include `"Task"`**. Context goes **explicitly in the prompt**. `AgentDefinition` = description, system prompt, tool restrictions. Pass full prior findings to the synthesiser; use structured formats that separate content from metadata (URL, doc name, page). **Parallel = several `Task` calls in one response.** Give goals and quality criteria, not step-by-step procedures. | [exam-guide p.6] |
| 1.4 | Enforcement and handoff | Programmatic enforcement (hooks, prerequisite gates) vs prompt guidance: prompts have a **non-zero failure rate**, so use code when compliance must be deterministic (e.g. verify identity before a refund). Block `process_refund` until `get_customer` returns a verified ID. Split multi-concern requests into items and investigate in parallel. Handoff summary for humans: customer ID, root cause, amount, recommended action (the human has no transcript). | [exam-guide p.7] |
| 1.5 | Agent SDK hooks | `PostToolUse`: transform tool **results** before the model sees them (normalise Unix/ISO 8601/status codes). Pre-call interception: block policy violations (refund > $500) and redirect to escalation. Hooks = deterministic guarantees; prompts = probabilistic. | [exam-guide p.7] |
| 1.6 | Task decomposition | **Prompt chaining** (fixed sequence) for predictable multi-aspect reviews, e.g. per-file passes then a cross-file integration pass (avoids attention dilution). **Dynamic decomposition** for open-ended work: map the structure → find high-impact areas → prioritised plan that adapts. | [exam-guide p.8] |
| 1.7 | Session state, resume, fork | `--resume <session-name>` continues a named session. `fork_session` branches from a shared baseline to compare approaches. After code changes, tell the resumed session which files changed. If tool results are **stale**, start fresh with a structured summary instead of resuming. | [exam-guide p.8–9] |

## Common traps

| Wrong answer pattern | Why it's wrong | Source |
|---|---|---|
| Stop the loop when the text says "done", or when text content appears | Parse `stop_reason`, not natural language | [exam-guide p.5] |
| Iteration cap as the **main** stopping mechanism | A cap is a safety limit only | [exam-guide p.5] |
| Assume subagents "know" the conversation | Context is isolated; pass it explicitly | [exam-guide p.5–6] |
| Spawn parallel subagents across separate turns | That's sequential; use several `Task` calls in **one** response | [exam-guide p.6] |
| Enforce a financial rule with a stronger system prompt | Use a hook or prerequisite gate | [exam-guide p.7] |
| Resume a session whose tool results are stale | Start fresh with an injected summary | [exam-guide p.8] |

## Seen in my code

| What | Where |
|---|---|
| Hand-written loop on `stop_reason`, `max_turns` as safety limit, escalation | `support_agent/loop.py` |
| `PreToolUse` hook blocks refunds > limit and opens a ticket (1.4, 1.5) | `support_agent/escalation_agent.py` |
| Coordinator with only `Task`; 3 `AgentDefinition`s; parallel `Task` calls `[2, 1]` (1.2, 1.3) | `research/research_agent.py` |
| Lesson: the model passed `run_in_background: true`, overriding `background=False`; fixed with a hook using `updatedInput` | [runs ex4-background-fix.log] |

## Related
[D2](d2-tool-design-mcp.md) (tool distribution) · [D5](d5-context-reliability.md) (error propagation, provenance)
