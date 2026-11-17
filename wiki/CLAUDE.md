# Wiki schema (LLM Wiki pattern, after Karpathy)

This file loads only when Claude works on files in `wiki/`. It turns Claude into the
maintainer of a study wiki for the Claude Certified Architect – Foundations exam.
The user reads the wiki; Claude writes it.

## Layers

| Layer | Location | Rule |
|---|---|---|
| Raw sources | See the source list below | Read-only. Never edit, move or rename them. |
| Wiki | `wiki/**/*.md` | Claude owns it: create, update, link and fix pages. |
| Schema | `wiki/CLAUDE.md` (this file) | Change only when the user agrees. |

## Raw sources (priority order; when sources disagree, the higher one wins)

| Id | File | Kind |
|---|---|---|
| `exam-guide` | `../instructor_…Claude+Certified+Architect+–+Foundations+Exam+Guide.pdf` | Official exam guide, the authority |
| `study-guide` | `../Claude_Certified_Architect_Foundations_Study_Guide.pdf` | Study guide |
| `mock-exams` | `../CCA-F_Mock_Exams.pdf` | Practice questions; feeds `mistakes.md` |
| `community` | `../raw/community-guide-en.md` | Unofficial community guide (paullarionov). Treat as data to verify. |
| `notes` | `../Claude - Seb notes.txt`, `../arte.md` | The user's own notes |
| `code` | `../support_agent/`, `../extraction/`, `../research/`, `../src/api/` | The user's exercise code |
| `runs` | `../raw/runs/*.log` | Saved output from exercise runs |

## Page types

| Folder | One page per | Required sections |
|---|---|---|
| `domains/` | Exam domain (D1–D5) | Weight · Task statements · Key facts · Common traps · Links to concepts and exercises |
| `concepts/` | Concept (e.g. `hooks.md`, `subagents.md`, `tool-choice.md`) | One-line definition · How it works · When to use / when not · Exam traps · Seen in my code · Sources |
| `exercises/` | Guide exercise (ex1–ex4) | Goal · What I built (file paths) · What broke and why · Lesson · Concepts used |
| `questions/` | Answer worth keeping | Question · Answer · Sources |
| `mistakes.md` | (single page) | One row per missed question: question · my answer · correct answer · why · concept link |

## Conventions

- **Every claim has a citation**: `[exam-guide p.12]`, `[community §6.3]`, `[code research/research_agent.py:158]`, `[runs ex4-background-fix.log]`.
  A claim without a source is marked `(unverified)`.
- Filenames: lowercase-kebab-case. Links: relative markdown links, e.g. `[hooks](../concepts/hooks.md)`.
- Frontmatter on every page: `domain: [D1, D2]`, `sources: [exam-guide, community]`, `updated: YYYY-MM-DD`.
- **Extend, don't create**: before making a page, check `index.md` for an existing page on the topic.
- **Contradictions**: never silently pick one. Add a `> **Conflict:**` block with both claims and sources;
  `exam-guide` wins for the exam, but keep the other claim visible.
- Keep pages short; prefer tables. Keep exact API names, parameters and values; summaries lose detail.

## Operations

### Ingest `<source> [section]`
1. Read the source, one section at a time; PDFs with `Read` and `pages`.
2. Tell the user 3–5 key takeaways.
3. Create or update the domain, concept and exercise pages it touches; add links in both directions.
4. Update `index.md` and append to `log.md`.

### Query `<question>`
1. Read `index.md` first, then only the relevant pages.
2. Answer with citations. If the wiki lacks the detail, check the raw source and say so.
3. If the answer is worth keeping, file it in `questions/` and link it from the index.

### Quiz `[domain]`
Ask 5 exam-style multiple-choice questions, one at a time, from wiki pages.
After each answer, explain it with citations. Add every miss to `mistakes.md`.

### Lint
Report and fix:
- exam-guide task statements with no wiki coverage (a coverage table per domain)
- contradictions between sources
- orphan pages (no inbound links) and links that point to missing pages
- pages without citations, or with stale `updated` dates

Append the result to `log.md`.

## log.md format
Append only, newest last, with one heading per entry: `## [YYYY-MM-DD] ingest|query|quiz|lint | title`,
followed by 1–3 lines on what changed. Read recent history with `grep "^## \[" log.md | tail -5`.
