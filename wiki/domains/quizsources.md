# Quiz Sources Registry

This file is the authoritative registry for study-quiz source provenance in this repository.

## Generation and provenance rules

1. Generate quiz questions only from sources listed in this registry and explicitly marked **Active**.
2. Preserve each source's terminology, facts, boundaries, and distinctions. Do not silently supplement answers with general knowledge or other files.
3. Every generated question must carry:
   - a unique question ID within its attempt;
   - a source ID from this registry;
   - the exact source task/section number (or page/line locator when no numbered task exists);
   - a link to the source.
4. Every response record in `testresultscratchpad.md` and the corresponding attempt file must repeat the source ID, source task/section number, and source URL.
5. If a concept cannot be mapped to a specific source locator, do not quiz it until the source registry is corrected.
6. On completion of all questions in an attempt/source set, update that source's status below. Do not mark a source complete merely because one quiz set was completed if more registered content remains untested.

## Registered sources

### SRC-D3-CONFIG — D3 Claude Code Configuration & Workflows
- **Status:** Active — quiz set in progress
- **Canonical source:** [D3 Claude Code Configuration & Workflows](./d3-claude-code-config.md)
- **Source URL:** https://github.com/rsebasten/claude-architect-study/blob/main/wiki/domains/d3-claude-code-config.md
- **Scope:** Task statements 3.1–3.6 and the associated key facts and common traps in the D3 reference.
- **Source locators:**
  - **SRC-D3-CONFIG-3.1** — CLAUDE.md hierarchy, imports, modular rules, and memory inspection.
  - **SRC-D3-CONFIG-3.2** — Slash command and skill locations, frontmatter, context isolation, and usage distinction.
  - **SRC-D3-CONFIG-3.3** — Path-specific rules, YAML path globs, conditional loading, and when to use them.
  - **SRC-D3-CONFIG-3.4** — Plan mode versus direct execution; Explore subagent.
  - **SRC-D3-CONFIG-3.5** — Iterative refinement, examples, test-driven prompting, interview pattern, and batching related issues.
  - **SRC-D3-CONFIG-3.6** — CI/CD non-interactive execution, structured output, independent review, re-review, and avoiding duplicate tests.
- **Quiz coverage status:** In progress
- **Completed attempts:** None
- **Current attempt:** D3-A1
- **Completion rule:** Mark the source status **Completed** only after all questions in D3-A1 have been answered and the attempt and scratchpad records have been committed. If later D3 coverage is planned, record it as a new attempt and update status accordingly.

## Naming convention

- Source IDs are stable and must never be reused for a different source.
- Task locator IDs are formed as `<SOURCE-ID>-<task-number>`.
- Attempt IDs use a domain prefix and sequence, e.g. `D3-A1`.
- Question IDs use the attempt plus a sequence, e.g. `D3-A1-Q01`.
