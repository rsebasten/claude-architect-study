---
paths:
  - "mcp_servers/**/*.py"
  - ".mcp.json"
---

# MCP tool conventions

- Tool descriptions say when to use the tool AND when to use its look-alike instead.
- Failures are structured: `{errorCategory, isRetryable, description}` with `isError` set.
  Categories: `validation`, `not_found`, `transient`, `policy`.
- Servers here are read-only; actions with side effects (refunds) need a code-enforced hook.
- Data is fictional. Credentials, if ever needed, come from `${ENV_VAR}` expansion in
  `.mcp.json` - never hard-coded or committed.
