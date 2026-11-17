---
paths:
  - "support_agent/**/*.py"
  - "*_agent.py"
---

# Agent loop conventions

- Agentic loops must exit on `stop_reason`, with `max_turns` only as a safety limit.
- Print `stop_reason` on every turn.
- Return all `tool_result` blocks for a turn in a single user message, with matching `tool_use_id`.
- Handle `max_tokens` and `refusal` explicitly; escalate instead of failing silently.
- Keep `loop.py`, `agent_sdk.py` and `escalation_agent.py` behaviorally parallel when changing one.
