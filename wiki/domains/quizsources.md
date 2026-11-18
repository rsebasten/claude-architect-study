# Quiz Sources Registry

This registry controls which source material may be used to create quizzes.

## Mandatory quiz rules

1. **Do not invent, paraphrase, adapt, or write new questions or answer choices.**
2. Present the source's question prompt and all answer choices verbatim, preserving wording and order.
3. Use only questions that actually appear in a registered source. Never create distractors or rewrite choices.
4. Preserve the source's supplied correct answer and explanation. If the source does not supply an answer key or explanation, say so; do not infer one silently.
5. Every question record must include its stable source ID, original question number (or source line locator if the source has no printed number), section, and URL.
6. Every answer in `testresultscratchpad.md` and the corresponding attempt file must record the source ID and original source question number/locator.
7. Study notes may be used to explain a source question only when clearly labeled as supporting notes; they are not a source of quiz questions.
8. If exact source wording or answer choices cannot be verified, stop and ask rather than generate replacements.

## Registered quiz sources

### SRC-CCA-GUIDE — Claude Certified Architect Guide (English)
- **Status:** Active
- **Role:** Authoritative question source
- **Canonical source:** [guide_en.md](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md)
- **Source URL:** https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md
- **Verified question count:** 88 numbered question blocks: 12 in “Examples of Exam Questions with Explanations” and 76 in “Practice Test” (checked 2026-11-18).
- **Question cache:** [claude-certified-architect-guide_en-questions.md](./claude-certified-architect-guide_en-questions.md) — verbatim local extraction; use this file for quizzes so the external source does not need to be fetched for every question.
- **Question locator convention:** Use stable IDs `EXAMPLE-Q01`–`EXAMPLE-Q12` and `PRACTICE-Q01`–`PRACTICE-Q76`; preserve original question numbers and source line locators. Re-extract and verify the source revision before replacing this cache.
- **Content rule:** Source prompt, options, correct answer, and explanation must be copied from the guide exactly. Do not create new questions or options.
- **Progress status:** Not started
- **Cached question count:** 88
- **Completed questions:** 0/88
- **Current attempt:** None

### SRC-D3-CONFIG — D3 Claude Code Configuration & Workflows
- **Status:** Supporting reference only — not eligible as a quiz-question source
- **Canonical source:** [d3-claude-code-config.md](./d3-claude-code-config.md)
- **Source URL:** https://github.com/rsebasten/claude-architect-study/blob/main/wiki/domains/d3-claude-code-config.md
- **Role:** Supporting study notes only. It may help explain concepts after a source question, but must never be used to author or replace a question or answer choice.
- **Question-generation status:** Disabled

## Attempt and question ID conventions

- Source IDs are stable and must never be reused.
- Attempt IDs use a source prefix and sequence, e.g. `CCA-A1`.
- Each question record uses the source's original ordinal and locator, e.g. `SRC-CCA-GUIDE / Source Q01 / guide_en.md line 1965`.
- Local attempt sequence numbers must never be represented as original source question numbers.
