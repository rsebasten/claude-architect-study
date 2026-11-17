---
description: Syntax-check every Python file and review agent-loop conventions
allowed-tools: Bash(python3 -m py_compile:*), Bash(find:*), Read, Grep
---

1. Run `python3 -m py_compile` on every `.py` file in the project (skip `__pycache__`).
2. For each agent script, check it against `.claude/rules/agent-loops.md`; for files in
   `mcp_servers/`, check `.claude/rules/mcp-tools.md`.
3. Report a table: file | compiles | rule violations (with `file:line`). Do not edit files.
