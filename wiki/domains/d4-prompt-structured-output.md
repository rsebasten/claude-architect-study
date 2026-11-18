---
domain: [D4]
sources: [exam-guide, code]
updated: 2026-11-17
---
# D4 Prompt Engineering & Structured Output

**Weight:** 20% [exam-guide p.3]

## Task statements

| # | Task statement | Key facts to know | Source |
|---|---|---|---|
| 4.1 | Explicit criteria | Specific categorical criteria ("flag only when the comment contradicts the code") beat vague ones ("check comments are accurate", "be conservative", "only high-confidence"). False positives destroy trust in the accurate categories too. Temporarily **disable** noisy categories while you fix them. Define severity levels with concrete code examples. | [exam-guide p.16] |
| 4.2 | Few-shot prompting | Most effective for consistent format when instructions alone vary. **2–4 targeted examples** for ambiguous cases, **showing the reasoning** for the chosen option over alternatives. Helps generalisation to new patterns, fewer false positives (acceptable vs real issue), and less hallucination or null-filling in extraction across varied document structures. | [exam-guide p.16–17] |
| 4.3 | Structured output via tool use | `tool_use` + JSON schema = most reliable; **removes syntax errors, not semantic ones** (totals that don't add up, wrong fields). `tool_choice`: `"auto"` may return text · `"any"` must call some tool (use when several schemas exist and the doc type is unknown) · forced `{"type":"tool","name":"extract_metadata"}` to run one first. **Nullable optional fields** stop fabrication. Enums with `"unclear"`, and `"other"` + detail field. Add format-normalisation rules to the prompt. | [exam-guide p.17–18] |
| 4.4 | Validation, retry, feedback | Retry with **document + failed extraction + specific errors**. Retry fixes format or structure errors, **not missing information** (e.g. data only in an external doc). `detected_pattern` field to analyse dismissed findings. Self-check fields: `calculated_total` vs `stated_total`, `conflict_detected`. | [exam-guide p.18] |
| 4.5 | Batch processing | **Message Batches API: 50% cheaper, up to 24h, no latency SLA.** For non-blocking jobs (overnight, weekly), **not** pre-merge checks. **No multi-turn tool calling** inside a batch request. `custom_id` correlates request and response. Resubmit only failures (by `custom_id`), e.g. chunk oversized docs. Refine the prompt on a sample first. SLA maths: 24h batch + 4h submission windows = 30h SLA guaranteed. | [exam-guide p.18–19] |
| 4.6 | Multi-instance and multi-pass review | Self-review is weak (the model keeps its own reasoning). An **independent instance** beats self-review instructions or extended thinking. Per-file passes + a cross-file integration pass. A verification pass with self-reported confidence per finding, for routing. | [exam-guide p.19] |

## Common traps

| Wrong answer pattern | Why it's wrong | Source |
|---|---|---|
| "Be conservative" to reduce false positives | Use explicit categorical criteria | [exam-guide p.16] |
| Strict schema means the data is correct | Only shape is guaranteed; validate semantics yourself | [exam-guide p.17] |
| Make every field required | Forces made-up values; use nullable fields | [exam-guide p.17] |
| Keep retrying when the info isn't in the document | Retry can't create missing data; route to a human | [exam-guide p.18] |
| Batch API for a pre-merge check | Blocking workflow; use the synchronous API | [exam-guide p.18–19] |
| Bigger model or context window for a 14-file review | Split into per-file plus integration passes | [exam-guide p.19, p.33] |
| Batch with tool calls mid-request | Not supported | [exam-guide p.18] |

## Seen in my code

| What | Where |
|---|---|
| Strict `record_extraction` tool: nullable fields, `"other"` + `*_detail` enums (4.3) | `extraction/pipeline.py` |
| `validate()` = Pydantic + cross-field rules (`total_mismatch`); retry loop that stops when the same error recurs (4.4) | `extraction/pipeline.py` |
| `table-004`: line items 1,900 vs total 2,100, so retry can't fix it → `not_fixable` (4.4) | `extraction/documents.py` |
| Few-shot toggle `--no-few-shot` (4.2); confidence routing at 0.8 | `extraction/pipeline.py` |
| `run_batch()`: 100 docs, failures by `custom_id`, chunked resubmit, SLA maths (4.5) | `extraction/pipeline.py` |

> **Conflict (real world vs exam):** forced `tool_choice` returned 400 on Opus 5.5 in Exercise 3, and the gateway returned 404 for `/v1/messages/batches`.
> Both are environment limits. **For the exam, answer per the guide.**

## Related
[D2](d2-tool-design-mcp.md) (`tool_choice`) · [D5](d5-context-reliability.md) (5.5 confidence calibration)
