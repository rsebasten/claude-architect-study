# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Study code for the Claude Certified Architect – Foundations exam: small, self-contained Python scripts that demonstrate agent loops and tool use. Not a package — no build step; the only unit tests are in `src/api/` (they exist mainly so the `api` and `tests` path rules have files to match).

Coding standards are described in @./standards/coding-style.md
Test requirements are in @./standards/testing-requirements.md

## Environments

No virtualenv: run every script with the global `python3`, which is uv-managed Python 3.12 in `~/.local/bin` (set up with `uv python install 3.12 --default`). It has `claude-agent-sdk` (needs Python >= 3.10) and `anthropic==0.125.0` with `httpx`, installed via `uv pip install --system --break-system-packages --python 3.12 ...`; plain `pip install` is blocked on this interpreter. Keep `anthropic` below 1.0 unless `loop.py` is migrated: 1.x moves to `httpx2` and rejects the `httpx.Client` that `loop.py` passes in.

## Commands

```bash
python3 support_agent/loop.py ["question"]
python3 support_agent/agent_sdk.py ["question"]
python3 support_agent/escalation_agent.py [scenario | "question"]
python3 get_booking_agent.py ["question"]   # needs ANTHROPIC_API_KEY
python3 extraction/pipeline.py [doc_id ...] [--no-few-shot]   # Exercise 3, live
python3 extraction/pipeline.py batch [--live] [--sla-hours N]  # dry run unless --live
python3 research/research_agent.py [--timeout] [--sequential]  # Exercise 4, live
python3 mcp_servers/bookings_server.py --list        # list the MCP server's tools
python3 -m py_compile <file>                          # syntax check after every edit
(cd src/api && python3 -m unittest test_bookings_api.py)  # unit tests for the API handlers
```

`MODEL=...` env var overrides the model in `loop.py`, `agent_sdk.py`, and `get_booking_agent.py` (e.g. `MODEL=us.anthropic.claude-opus-5-5` for gateways that want Bedrock-style IDs).

## Auth

No API key is required for `loop.py` / `agent_sdk.py`:
- `loop.py` (`_claude_code_client`) uses `ANTHROPIC_API_KEY` if set; otherwise it rebuilds the Claude Code CLI's gateway config from `~/.claude/settings.json` — runs `apiKeyHelper` for a token, applies `ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_HEADERS`, and `NODE_EXTRA_CA_CERTS`.
- `agent_sdk.py` launches the Claude Code CLI under the hood, so it inherits the same settings automatically.
- `get_booking_agent.py` uses a bare `anthropic.Anthropic()` and defaults to `claude-opus-5-5`.

## Architecture

The scripts are the same weather/time (or booking) agent implemented at different abstraction levels — keep them behaviorally parallel when editing one:

- `support_agent/loop.py` — hand-written Messages API loop (the guide's "Figure 4"): `run_agent` → `dispatch` via `HANDLERS` → `ToolOutput(text, is_error)`; exits on `stop_reason`, raises `TruncatedOutput` on `max_tokens`, calls `escalate` when `max_turns` is exhausted. `FLAKY_WEATHER` makes the first London lookup fail to exercise `is_error` retries.
- `support_agent/agent_sdk.py` — the same tools as in-process MCP tools (`create_sdk_mcp_server`, exposed as `mcp__support__*`), built-in tools disabled (`tools=[]`), and a `PreToolUse` hook that denies `get_time`; prints the denial from both the message stream and the on-disk session JSONL transcript.
- `support_agent/escalation_agent.py` — guide Exercise 1 (Agent SDK): four MCP tools (`get_booking` vs `search_bookings` is the deliberate look-alike pair), structured errors `{errorCategory, isRetryable, description}`, and a `PreToolUse` hook that blocks refunds over `REFUND_LIMIT_USD` and opens an escalation ticket. `SCENARIOS` holds the test prompts; `reset_data()` runs before each. Uses `setting_sources=[]` plus `auth_only_settings()` so user CLAUDE.md/plugins don't leak into the agent while gateway auth still works.
- `get_booking_agent.py` — single-tool airline-support variant of the manual loop with input validation in `dispatch`.

- `extraction/pipeline.py` — guide Exercise 3 (Messages API, not an agent): strict `record_extraction` tool (nullable fields, optional `po_number`, enums with `"other"` + `*_detail`), `validate()` = Pydantic + cross-field rules strict schemas can't express, `extract()` validation-retry loop that stops when the same error recurs (source problem), few-shot toggle, confidence routing + accuracy by doc type/field, and `run_batch()` (100 docs, failures by `custom_id`, chunked resubmit, SLA math). Reuses `loop.client` for auth; `documents.py` holds fictional samples with ground truth.
- `research/research_agent.py` — guide Exercise 4 (Agent SDK multi-agent): coordinator has only `Task` (`tools=["Task"]`) and three `AgentDefinition`s — `web_researcher` + `doc_analyst` (parallel, `background=False` plus a hook that rewrites `run_in_background: true` to false via `updatedInput`, so the Task result is the subagent's JSON) then `synthesizer` (no tools). Subagent JSON contract: `findings[{claim, evidence_excerpt, source_url, source_name, publication_date}]`, `status`, `error`, `coverage_note`. `PreToolUse` hooks deny unknown `subagent_type`s and research-tool calls without `agent_id` (coordinator). `--timeout` makes `read_document` time out on one doc (structured error → `status: partial`). Parallelism is counted per `message_id` (the SDK splits blocks into separate `AssistantMessage`s). `corpus.py` holds the fictional Lumen Bay sources with planted conflicts (41% vs 34%, $18 vs $21).
- `mcp_servers/bookings_server.py` — read-only stdio MCP server (mcp 2.x `MCPServer`) with the same fictional bookings; registered in `.mcp.json` as `bookings`.

## Claude Code config

| What | Where | Notes |
|---|---|---|
| Path-specific rules | `.claude/rules/*.md` | Load only when a file matching `paths:` is read: `agent-loops` (agent scripts), `mcp-tools` (`mcp_servers/`), `api` (`src/api/**/*`), `tests` (`**/*.test.*`, `test_*.py`) |
| Custom command | `.claude/commands/check.md` | `/check`: syntax-check and rule review, no edits |
| Skill | `.claude/skills/scenario-report/` | `/scenario-report [name]`; `context: fork` keeps the raw trace out of the main session; `allowed-tools` limits it to the one script |
| Study wiki | `wiki/` + skill `.claude/skills/wiki/` | LLM Wiki pattern: `/wiki ingest\|query\|quiz\|lint`. Schema in `wiki/CLAUDE.md` (loads only when working in `wiki/`); raw sources read-only in `raw/` and the root PDFs |
| MCP server | `.mcp.json` (project, shared) | `bookings`, `BOOKINGS_ENV=${BOOKINGS_ENV:-demo}`; secrets via `${VAR}` expansion only |
| MCP override | `~/.claude.json` (local scope, private) | Same name `bookings`, `BOOKINGS_ENV=personal`; local beats project. Remove with `claude mcp remove bookings -s local` |

`arte.md`, `Claude - Seb notes.txt`, the PDFs and `raw/` are personal notes and exam material, not code.
