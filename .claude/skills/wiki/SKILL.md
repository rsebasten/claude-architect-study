---
name: wiki
description: Maintain the exam-study LLM wiki in wiki/ - ingest a source, answer a question from the wiki, quiz the user, or lint the wiki. Use when the user mentions the wiki, ingesting notes or guides, quizzing, or checking study coverage.
argument-hint: "ingest <source> [section] | query <question> | quiz [D1-D5] | lint"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(grep:*), Bash(ls:*)
---

Read `wiki/CLAUDE.md` first: it is the schema (layers, source ids, page types, citation rules,
operations). Then run the operation in `$ARGUMENTS` exactly as the schema describes it.

- `ingest <source id> [section]`: source ids are listed in the schema. Do one section per run;
  for a PDF, read only the pages for that section.
- `query <question>`: start from `wiki/index.md`.
- `quiz [domain]`: interactive, so ask one question and wait for the user's answer.
- `lint`: report first, then fix what can be fixed without the user's input.

Always finish by appending to `wiki/log.md` and telling the user, in a short table,
which pages were created or updated.
