---
domain: [D3]
sources: [exam-guide, code]
updated: 2026-11-17
---
# D3 Claude Code Configuration & Workflows

**Weight:** 20% [exam-guide p.3]

## Task statements

| # | Task statement | Key facts to know | Source |
|---|---|---|---|
| 3.1 | CLAUDE.md hierarchy | **User** `~/.claude/CLAUDE.md` (only you, not in git) · **project** `CLAUDE.md` or `.claude/CLAUDE.md` · **directory** (subfolder `CLAUDE.md`). `@import` keeps it modular (import only the relevant standards per package). `.claude/rules/` splits a monolithic file (`testing.md`, `api-conventions.md`). **`/memory`** shows which memory files are loaded. Typical diagnosis: a new teammate lacks instructions because they're user-level. | [exam-guide p.12–13] |
| 3.2 | Slash commands and skills | Commands: project `.claude/commands/` (shared) vs user `~/.claude/commands/`. Skills: `.claude/skills/<name>/SKILL.md` with frontmatter **`context: fork`** (isolated subagent context, keeps verbose output out of the main session), **`allowed-tools`** (restrict tools), **`argument-hint`** (prompt for parameters). Personal variants go in `~/.claude/skills/` **under a different name**. Skills = on demand; CLAUDE.md = always loaded. | [exam-guide p.13] |
| 3.3 | Path-specific rules | `.claude/rules/*.md` with YAML `paths:` globs (e.g. `["terraform/**/*"]`, `**/*.test.tsx`). **Loads only when editing matching files**, saving tokens. Better than subfolder CLAUDE.md when files are **spread across directories**. | [exam-guide p.13–14] |
| 3.4 | Plan mode vs direct execution | **Plan mode**: large or multi-file changes, several valid approaches, architecture decisions (microservice split, migration of 45+ files). **Direct**: simple, well-scoped work (one-file bug fix with a stack trace, one validation check). Combine: plan, then execute. The **Explore subagent** isolates verbose discovery to protect context. | [exam-guide p.14] |
| 3.5 | Iterative refinement | 2–3 concrete **input/output examples** beat prose. **Test-driven**: write tests first, share failures. **Interview pattern**: Claude asks questions first in unfamiliar domains. Send **interacting** issues in one message; fix **independent** issues one at a time. | [exam-guide p.14–15] |
| 3.6 | CI/CD | **`-p` / `--print`** = non-interactive (stops CI hanging). **`--output-format json` + `--json-schema`** = machine-readable findings for PR comments. CLAUDE.md gives CI its project context. Review with an **independent instance**, not the session that wrote the code. On re-review, include prior findings and report only new or unresolved ones. Give existing tests as context to avoid duplicate tests. | [exam-guide p.15–16] |

## Common traps

| Wrong answer pattern | Why it's wrong | Source |
|---|---|---|
| Team instructions in `~/.claude/CLAUDE.md` | User-level, not shared | [exam-guide p.12] |
| Subfolder CLAUDE.md for test conventions spread everywhere | Use a `.claude/rules/` glob like `**/*.test.tsx` | [exam-guide p.14, p.30] |
| Team command in `~/.claude/commands/` | Use project `.claude/commands/` | [exam-guide p.29] |
| `CLAUDE_HEADLESS=true` or redirecting stdin to stop CI hanging | The flag is **`-p`** | [exam-guide p.32] |
| Plan mode for a one-line fix / direct execution for a 45-file migration | Match the mode to scope and ambiguity | [exam-guide p.14] |
| The same session reviews its own code | Use an independent review instance | [exam-guide p.15] |

## Seen in my code

| What | Where |
|---|---|
| Project CLAUDE.md with `@./standards/...` imports (3.1) | `CLAUDE.md` |
| 4 path-scoped rules: `agent-loops`, `api`, `mcp-tools`, `tests` (3.3) | `.claude/rules/` |
| `/check` command (3.2) | `.claude/commands/check.md` |
| `scenario-report` skill with `context: fork` + `allowed-tools`; `wiki` skill with `argument-hint` (3.2) | `.claude/skills/` |
| Subfolder CLAUDE.md that loads only in `wiki/` (3.1) | `wiki/CLAUDE.md` |
| Plan mode used for the `get_booking_agent.py` model fix (3.4) | Exercise 2 |

## Related
[D2](d2-tool-design-mcp.md) (MCP scopes) · [D5](d5-context-reliability.md) (`/compact`, Explore subagent)
