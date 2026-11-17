---
name: scenario-report
description: Run escalation_agent.py scenarios and report tool calls, retries, hook decisions, stop_reason and cost. Use when asked to run, test, or check the escalation agent's scenarios.
argument-hint: "[scenario name | \"custom question\"]"
context: fork
allowed-tools: Bash(python3 support_agent/escalation_agent.py:*), Read
---

Run `python3 support_agent/escalation_agent.py $ARGUMENTS` (no arguments = all scenarios).
Read `support_agent/escalation_agent.py` only if you need to explain a result.

Return ONLY this report - the raw trace stays in this forked context:

| scenario | tools called | is_error results | retry correct per isRetryable? | hook decision | final stop_reason | cost |

Then list, at most 5 bullets:
- any final answer that contradicts a tool result (quote both)
- any escalation ticket opened, with its source (agent / hook / runtime)

Do not edit files.
