---
domain: [D2]
sources: [exam-guide, code]
updated: 2026-11-17
---
# D2 Tool Design & MCP Integration

**Weight:** 18% [exam-guide p.3]

## Task statements

| # | Task statement | Key facts to know | Source |
|---|---|---|---|
| 2.1 | Tool interfaces and descriptions | **Descriptions are the main way the model picks tools.** Include input formats, example queries, edge cases, and when to use this tool vs similar ones. Overlapping descriptions cause misrouting (`analyze_content` vs `analyze_document`). Fixes: rename (`analyze_content` → `extract_web_results`) or split generic tools (`extract_data_points`, `summarize_content`, `verify_claim_against_source`). Keyword-heavy system prompts can override good descriptions. | [exam-guide p.9] |
| 2.2 | Structured MCP errors | MCP **`isError`** flag. Categories: **transient** (timeout, unavailable), **validation** (bad input), **business** (policy), **permission**. Return `errorCategory`, `isRetryable`, a readable description; business-rule errors get `retriable: false` plus a customer-friendly message. A generic "Operation failed" blocks recovery. Subagents retry transient errors locally and propagate only what they can't fix, with partial results. **Access failure ≠ valid empty result.** | [exam-guide p.9–10] |
| 2.3 | Tool distribution and `tool_choice` | Too many tools (18 vs 4–5) hurts selection. Agents misuse tools outside their role (a synthesiser doing web search). Scope tools per role, plus limited cross-role tools for frequent needs (`verify_fact`). Replace generic tools with constrained ones (`fetch_url` → `load_document`). **`tool_choice`: `"auto"`, `"any"` (must call some tool), forced `{"type":"tool","name":"..."}`.** Force a tool to run first (e.g. `extract_metadata`), then continue in later turns. | [exam-guide p.10–11] |
| 2.4 | MCP servers in Claude Code and agents | **Project `.mcp.json`** (shared) vs **user `~/.claude.json`** (personal or experimental). `${GITHUB_TOKEN}`-style env expansion keeps secrets out of git. Tools from **all** configured servers are discovered at connection time and available together. **MCP resources** expose catalogues (issues, docs, schemas) and cut exploratory calls. Detailed descriptions stop the agent preferring Grep over a better MCP tool. Prefer community servers for standard integrations (Jira); build custom ones for team-specific workflows. | [exam-guide p.11] |
| 2.5 | Built-in tools | **Grep** = search file contents; **Glob** = match file paths (`**/*.test.tsx`); **Read/Write** = whole file; **Edit** = targeted change by unique text. If Edit fails on non-unique text, use Read + Write. Explore incrementally: Grep for entry points → Read to follow imports (don't read everything upfront). Trace wrappers: list exported names, then search for each. | [exam-guide p.11–12] |

## Common traps

| Wrong answer pattern | Why it's wrong | Source |
|---|---|---|
| Add few-shot examples or routing logic when two tools are confused | Fix the **descriptions** first; they're the main selection mechanism | [exam-guide p.9, p.28] |
| Return an empty success result on timeout | Hides the failure; return a structured error | [exam-guide p.10, p.31] |
| Give every agent every tool | Hurts reliability; scope per role | [exam-guide p.10] |
| Put a team MCP server in `~/.claude.json` | Not shared; use project `.mcp.json` | [exam-guide p.11] |
| Commit a token in `.mcp.json` | Use `${VAR}` expansion | [exam-guide p.11] |
| Grep to find files by name | That's Glob | [exam-guide p.11] |

> **Conflict:** the exam guide treats forced `tool_choice` (`any` / `{"type":"tool"}`) as available [exam-guide p.11, p.17].
> In my Exercise 3 run on Opus 5.5, forced `tool_choice` returned a **400**, so I used `auto` + a prompt instruction + `strict: true` [code extraction/pipeline.py].
> **For the exam, answer per the guide.** The model-specific limit is a real-world caveat only.

## Seen in my code

| What | Where |
|---|---|
| Look-alike tools `get_booking` vs `search_bookings` with differentiating descriptions (2.1) | `support_agent/escalation_agent.py` |
| Structured errors `{errorCategory, isRetryable, description}` (2.2) | `support_agent/escalation_agent.py`, `src/api/bookings_api.py` |
| Per-role tool scoping; synthesiser has no tools; hook stops the coordinator calling research tools (2.3) | `research/research_agent.py` |
| `.mcp.json` with `${BOOKINGS_ENV:-demo}` plus a local override in `~/.claude.json` (2.4) | `.mcp.json`, `mcp_servers/bookings_server.py` |

## Related
[D1](d1-agent-architecture.md) (hooks, subagents) · [D4](d4-prompt-structured-output.md) (`tool_choice` for structured output)
