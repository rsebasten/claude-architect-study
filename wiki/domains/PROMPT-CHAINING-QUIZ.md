# Prompt Chaining Quiz Wizard

A one-question-at-a-time practice wizard based on **Claude Certified Architect Study Guide §6.3 Prompt Chaining**, with related study notes stored beside the D3 domain reference.

## Format
- Seven multiple-choice questions, one correct answer each.
- Submit one answer at a time. Feedback includes right/wrong status, the correct answer, why it is correct, the misconception behind a wrong answer, and a remediation/escalation note.
- Ask for **more explanation** at any point to expand the current concept.
- Say **pause** to stop. Say **resume** to continue from the next unanswered question.
- A submitted answer is recorded in `testresultscratchpad.md` and the matching attempt file under `attempts/`. First answers determine first-attempt accuracy; subsequent retakes are logged as separate attempts.

## Key concepts tested
1. Sequential per-file analysis followed by a cross-file integration pass.
2. Attention dilution and consistent analysis quality.
3. Prompt chaining for predictable, repeatable tasks.
4. Dynamic decomposition for open-ended investigations where subtasks emerge from findings.
5. Fixed pipelines with known stages.
6. Cross-file integration issues such as inconsistent types and circular dependencies.
7. Selecting a decomposition strategy based on how much of the task is known up front.

## Source
- [Claude Certified Architect Guide — §6.3 Prompt Chaining](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_en.md#63-prompt-chaining)
- [Related D3 study notes](https://github.com/rsebasten/claude-architect-study/blob/main/wiki/domains/d3-claude-code-config.md)
- [Machine-readable question bank](./prompt-chaining-quiz.json)
- [Persistent answer scratchpad](./testresultscratchpad.md)
