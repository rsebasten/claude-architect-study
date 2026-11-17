#!/usr/bin/env python3
"""Exam guide Exercise 3: structured data extraction pipeline (Domains 4 and 5).

  python3 extraction/pipeline.py [extract] [doc_id ...] [--no-few-shot]
  python3 extraction/pipeline.py batch [--live] [--sla-hours N]

Pieces, in the order the guide lists them:
1. TOOL - extraction schema: required + optional fields, enum with "other" + detail,
   nullable fields. strict=True guarantees the *shape*; it cannot express ranges or
   cross-field rules (no minimum/maximum in strict schemas), so those live in validate().
2. extract() - validation-retry loop: on failure, the follow-up carries the document,
   the failed extraction (the assistant's tool_use) and the specific errors
   (an is_error tool_result). Tracks which errors a retry fixed and which it didn't.
3. FEW_SHOT - two examples with different layouts; --no-few-shot to compare.
4. run_batch() - Message Batches API for 100 docs; failures handled by custom_id,
   oversized docs chunked on resubmit, total time checked against an SLA.
5. route() + report() - field-level confidence routes to human review; accuracy is
   broken down by document type and field, including calibration of confidence.

Opus 5.5 rejects forced tool_choice ("any"/"tool"), so requests use "auto" + a prompt
instruction, and extract() re-prompts if no tool call comes back.
"""

import json
import os
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "support_agent"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from documents import SAMPLES, SCORED_FIELDS, make_batch_docs  # noqa: E402

MAX_RETRIES = 2              # validation retries after the first attempt
CONFIDENCE_THRESHOLD = 0.8   # any scored field below this goes to human review
MAX_DOC_CHARS = 20_000       # resubmit docs larger than this as chunks
BATCH_MAX_HOURS = 24         # Message Batches processing window (worst case)

# ---------------------------------------------------------------- 1. schema


def nullable(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


TOOL = {
    "name": "record_extraction",
    "description": (
        "Record the fields extracted from ONE invoice-like document. Call it exactly once "
        "per document. Use null for any field the document does not state - never infer "
        "or invent a value. Use 'other' plus the matching *_detail field when the value "
        "is not in the enum; otherwise set *_detail to null."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "vendor_name": nullable({"type": "string"}),
            "invoice_number": nullable({"type": "string"}),
            "invoice_date": nullable({"type": "string", "format": "date"}),
            "po_number": {"type": "string",
                          "description": "Optional: omit entirely if no PO is mentioned."},
            "currency": {"type": "string", "enum": ["USD", "EUR", "GBP", "other"]},
            "currency_detail": nullable({"type": "string"}),
            "category": {"type": "string",
                         "enum": ["software", "hardware", "travel", "services", "other"]},
            "category_detail": nullable({"type": "string"}),
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"description": {"type": "string"},
                                   "amount": nullable({"type": "number"})},
                    "required": ["description", "amount"],
                },
            },
            "total": nullable({"type": "number",
                               "description": "Total exactly as printed, even if it "
                                              "disagrees with the line items."}),
            "field_confidence": {
                "type": "object",
                "description": "0.0-1.0 per field: how sure you are the value (or null) "
                               "is what the document says.",
                "additionalProperties": False,
                "properties": {f: {"type": "number"} for f in SCORED_FIELDS},
                "required": SCORED_FIELDS,
            },
        },
        # po_number is the one optional field: absent from `required`.
        "required": ["vendor_name", "invoice_number", "invoice_date", "currency",
                     "currency_detail", "category", "category_detail", "line_items",
                     "total", "field_confidence"],
    },
}


class LineItem(BaseModel, extra="forbid"):
    description: str
    amount: float | None


class Extraction(BaseModel, extra="forbid"):
    vendor_name: str | None
    invoice_number: str | None
    invoice_date: date | None
    po_number: str | None = None
    currency: Literal["USD", "EUR", "GBP", "other"]
    currency_detail: str | None
    category: Literal["software", "hardware", "travel", "services", "other"]
    category_detail: str | None
    line_items: list[LineItem]
    total: float | None
    field_confidence: dict[str, float]


def validate(data: dict) -> list[dict]:
    """Pydantic (types/format) first, then rules a strict schema cannot express."""
    try:
        ext = Extraction.model_validate(data)
    except ValidationError as e:
        return [{"code": err["type"], "field": ".".join(map(str, err["loc"])),
                 "message": err["msg"]} for err in e.errors()]

    errors = []

    def add(code, field, message):
        errors.append({"code": code, "field": field, "message": message})

    for field, value in ext.field_confidence.items():
        if not 0.0 <= value <= 1.0:
            add("confidence_range", f"field_confidence.{field}", f"{value} is not in 0.0-1.0")
    for field in ("currency", "category"):
        detail = getattr(ext, f"{field}_detail")
        if getattr(ext, field) == "other" and not detail:
            add("other_without_detail", f"{field}_detail", f"{field} is 'other' but no detail given")
        if getattr(ext, field) != "other" and detail:
            add("detail_without_other", f"{field}_detail", f"detail set but {field} is not 'other'")
    amounts = [i.amount for i in ext.line_items]
    if ext.total is not None and amounts and None not in amounts:
        if abs(sum(amounts) - ext.total) > 0.01:
            add("total_mismatch", "total",
                f"line items sum to {sum(amounts):.2f} but total is {ext.total:.2f}")
    if ext.invoice_date and ext.invoice_date > date.today():
        add("future_date", "invoice_date", f"{ext.invoice_date} is in the future")
    return errors


# ---------------------------------------------------------------- 3. prompt + few-shot

SYSTEM_BASE = """You extract invoice data from business documents (tables, emails, receipts,
scans). Always answer by calling the record_extraction tool once.

Rules:
- Copy values as the document states them. Normalize dates to YYYY-MM-DD.
- If a field is not stated or is illegible, use null and give it low confidence.
  A plausible guess is worse than null.
- Record the total exactly as printed, even if the line items disagree with it."""

FEW_SHOT = """

<examples>
<example layout="table">
<document>
QUARRY LANE PRINTING  |  Inv QL-118  |  2026-04-02
Posters A2 x50 ....... USD 300.00
Delivery ............. USD  25.00
Total ................ USD 325.00
</document>
record_extraction: {"vendor_name": "Quarry Lane Printing", "invoice_number": "QL-118",
"invoice_date": "2026-04-02", "currency": "USD", "currency_detail": null,
"category": "services", "category_detail": null,
"line_items": [{"description": "Posters A2 x50", "amount": 300.0},
{"description": "Delivery", "amount": 25.0}], "total": 325.0,
"field_confidence": {"vendor_name": 0.98, "invoice_number": 0.97, "invoice_date": 0.97,
"currency": 0.99, "category": 0.8, "total": 0.99}}
</example>
<example layout="narrative">
<document>
Quick note from Sam at Fernhill Bikes: the courier e-bike rental for June was
SEK 2,400. No invoice number yet - accounts will follow up.
</document>
record_extraction: {"vendor_name": "Fernhill Bikes", "invoice_number": null,
"invoice_date": null, "currency": "other", "currency_detail": "SEK",
"category": "other", "category_detail": "equipment rental",
"line_items": [{"description": "Courier e-bike rental (June)", "amount": 2400.0}],
"total": 2400.0, "field_confidence": {"vendor_name": 0.9, "invoice_number": 0.95,
"invoice_date": 0.9, "currency": 0.95, "category": 0.6, "total": 0.95}}
</example>
</examples>
Note how the second example uses null for the missing number and date (the month
alone is not a date), and "other" + detail for values outside the enums."""


def request_params(doc_text: str, few_shot: bool = True) -> dict:
    """One request body, shared by the sync path and the batch path."""
    return {
        "model": os.environ.get("MODEL", "claude-opus-5-5"),  # same override as loop.py
        "max_tokens": 16000,
        "output_config": {"effort": "medium"},
        # The system prompt is identical for every doc, so cache it (batches too).
        "system": [{"type": "text", "text": SYSTEM_BASE + (FEW_SHOT if few_shot else ""),
                    "cache_control": {"type": "ephemeral"}}],
        "tools": [TOOL],  # tool_choice defaults to auto; Opus 5.5 rejects forcing it
        "messages": [{"role": "user", "content":
                      f"<document>\n{doc_text}\n</document>\n\n"
                      "Extract this document with the record_extraction tool."}],
    }


# ---------------------------------------------------------------- 2. validation-retry loop


def extract(doc: dict, few_shot: bool = True) -> dict:
    from loop import client
    params = request_params(doc["text"], few_shot)
    messages = params.pop("messages")
    attempts = []      # validation error lists, one per extraction the model returned
    last_input = None  # most recent extraction, kept even if it never validates

    for attempt in range(1 + MAX_RETRIES):
        resp = client.messages.create(**params, messages=messages)
        print(f"  [{doc['id']}] attempt {attempt + 1}: stop_reason={resp.stop_reason}")
        if resp.stop_reason in ("refusal", "max_tokens"):
            return outcome(doc, last_input, attempts, f"stopped: {resp.stop_reason}")

        call = next((b for b in resp.content
                     if b.type == "tool_use" and b.name == TOOL["name"]), None)
        messages.append({"role": "assistant", "content": resp.content})
        if call is None:  # auto does not guarantee a call
            if last_input is not None:  # it already extracted; text now = it's explaining
                break
            messages.append({"role": "user", "content":
                             "Please answer by calling the record_extraction tool."})
            continue

        last_input = call.input
        errors = validate(call.input)
        attempts.append(errors)
        if not errors:
            return outcome(doc, call.input, attempts)
        for e in errors:
            print(f"      invalid: {e['code']} ({e['field']}): {e['message']}")
        if len(attempts) > 1 and {e["code"] for e in errors} == {e["code"] for e in attempts[-2]}:
            print("      same errors after a retry -> source problem; stop retrying")
            break
        # The retry carries the document (still in messages), the failed extraction
        # (the assistant tool_use above) and the specific errors (this tool_result).
        messages.append({"role": "user", "content": [{
            "type": "tool_result", "tool_use_id": call.id, "is_error": True,
            "content": json.dumps({"validation_errors": errors, "instruction": (
                "Re-read the document and call record_extraction again with the "
                "problems fixed. If a problem comes from the document itself (it is "
                "inconsistent, or the value is absent), keep what the document says or "
                "use null, and set that field's confidence below 0.5.")}),
        }]})

    failure = "validation failed after retries" if attempts else "no tool call"
    return outcome(doc, last_input, attempts, failure)


def outcome(doc, data, attempts, failure=None) -> dict:
    """Classify errors: fixed by a retry (format slips) vs not (source problems)."""
    first = {e["code"] for e in attempts[0]} if attempts else set()
    last = {e["code"] for e in attempts[-1]} if attempts else set()
    return {"doc": doc, "data": data, "attempts": len(attempts), "failure": failure,
            "fixed_by_retry": sorted(first - last), "not_fixable": sorted(last)}


# ---------------------------------------------------------------- 5. routing + analysis


def route(result: dict) -> list[str]:
    """Reasons to send this extraction to a human (empty = auto-accept)."""
    if result["failure"]:
        return [result["failure"]] + [f"unresolved: {c}" for c in result["not_fixable"]]
    conf = result["data"]["field_confidence"]
    return [f"low confidence: {f}={conf[f]:.2f}" for f in SCORED_FIELDS
            if conf.get(f, 0) < CONFIDENCE_THRESHOLD]


def correct(field, got, expected) -> bool:
    if expected is None or got is None:
        return got is None and expected is None
    if field == "total":
        return abs(float(got) - float(expected)) < 0.01
    return str(got).strip().lower() == str(expected).strip().lower()


def report(results: list[dict]) -> None:
    by_type = defaultdict(lambda: [0, 0])
    by_field = defaultdict(lambda: [0, 0])
    calibration = {"high": [0, 0], "low": [0, 0]}  # accuracy split by confidence band
    print("\n| doc | type | attempts | fixed by retry | not fixable | route |")
    print("|---|---|---|---|---|---|")
    for r in results:
        reasons = route(r)
        print(f"| {r['doc']['id']} | {r['doc']['doc_type']} | {r['attempts']} | "
              f"{', '.join(r['fixed_by_retry']) or '-'} | {', '.join(r['not_fixable']) or '-'} | "
              f"{'HUMAN: ' + '; '.join(reasons) if reasons else 'auto-accept'} |")
        if not r["data"]:
            continue
        for f in SCORED_FIELDS:
            ok = correct(f, r["data"].get(f), r["doc"]["expected"][f])
            for bucket in (by_type[r["doc"]["doc_type"]], by_field[f]):
                bucket[0] += ok
                bucket[1] += 1
            band = "high" if r["data"]["field_confidence"].get(f, 0) >= CONFIDENCE_THRESHOLD else "low"
            calibration[band][0] += ok
            calibration[band][1] += 1
            if not ok:
                print(f"|   ↳ wrong {f}: got {r['data'].get(f)!r}, "
                      f"expected {r['doc']['expected'][f]!r} | | | | | |")

    def pct(pair):
        return f"{pair[0]}/{pair[1]} ({100 * pair[0] / pair[1]:.0f}%)" if pair[1] else "-"

    print("\nAccuracy by document type:  " + "  ".join(f"{t} {pct(v)}" for t, v in by_type.items()))
    print("Accuracy by field:          " + "  ".join(f"{f} {pct(v)}" for f, v in by_field.items()))
    print(f"Calibration: confidence >= {CONFIDENCE_THRESHOLD}: {pct(calibration['high'])}   "
          f"< {CONFIDENCE_THRESHOLD}: {pct(calibration['low'])}  "
          "(high-confidence fields should be ~100% correct, or the threshold is unsafe)")


# ---------------------------------------------------------------- 4. batch processing


def chunk(doc: dict) -> list[dict]:
    """Split an oversized doc by lines, repeating the 2-line header in every part."""
    lines = doc["text"].splitlines()
    header, body = lines[:2], lines[2:]
    parts, current = [], []
    for line in body:
        if sum(len(x) + 1 for x in header + current + [line]) > MAX_DOC_CHARS:
            parts.append(current)
            current = []
        current.append(line)
    parts.append(current)
    return [{**doc, "id": f"{doc['id']}-part{i + 1}", "text": "\n".join(header + p),
             "parent": doc["id"]} for i, p in enumerate(parts)]


def merge_parts(extractions: list[dict]) -> dict:
    """Scalars: first non-null across parts. Line items: concatenated. Confidence: min."""
    merged = {"line_items": [], "field_confidence": {}}
    for ext in extractions:
        for k, v in ext.items():
            if k == "line_items":
                merged[k] += v
            elif k == "field_confidence":
                for f, c in v.items():
                    merged[k][f] = min(c, merged[k].get(f, 1.0))
            elif merged.get(k) is None:
                merged[k] = v
    return merged


def to_requests(docs: list[dict]) -> list[dict]:
    return [{"custom_id": d["id"], "params": request_params(d["text"])} for d in docs]


def submit_and_collect(requests: list[dict], live: bool, sim_failures: dict) -> dict:
    """Returns {custom_id: ("succeeded", tool_input) | (error_type, None)}."""
    if not live:  # dry run: pretend every request succeeds except the planned failures
        return {r["custom_id"]: sim_failures.get(r["custom_id"], ("succeeded", None))
                for r in requests}
    import anthropic
    from loop import client, USING_GATEWAY
    try:
        batch = client.messages.batches.create(requests=requests)
    except anthropic.NotFoundError:
        sys.exit("Batches endpoint not found (404). "
                 + ("Your gateway doesn't expose /v1/messages/batches; set ANTHROPIC_API_KEY "
                    "to call the Anthropic API directly, or use the dry run." if USING_GATEWAY
                    else "Check the base URL and that your key can use the Batches API."))
    print(f"  submitted batch {batch.id} ({len(requests)} requests); polling every 30s")
    while (batch := client.messages.batches.retrieve(batch.id)).processing_status != "ended":
        print(f"    {batch.processing_status}: {batch.request_counts.processing} processing")
        time.sleep(30)
    out = {}
    for item in client.messages.batches.results(batch.id):  # any order: key by custom_id
        res = item.result
        if res.type == "succeeded":
            call = next((b for b in res.message.content if b.type == "tool_use"), None)
            out[item.custom_id] = ("succeeded", call.input if call else None)
        elif res.type == "errored":
            out[item.custom_id] = (res.error.error.type, None)
        else:  # canceled / expired
            out[item.custom_id] = (res.type, None)
    return out


def run_batch(live: bool, sla_hours: float) -> None:
    docs = {d["id"]: d for d in make_batch_docs(100)}
    started = time.time()
    print(f"Pass 1: {len(docs)} documents ({'LIVE' if live else 'dry run - no API calls'})")
    # Dry run injects one of each failure kind so the handling below is exercised.
    sim1 = {"doc-037": ("invalid_request_error", None),  # oversized
            "doc-011": ("overloaded_error", None), "doc-058": ("api_error", None),
            "doc-090": ("expired", None)}
    results = submit_and_collect(to_requests(docs.values()), live, sim1)

    failed = {cid: kind for cid, (kind, _) in results.items() if kind != "succeeded"}
    print(f"  succeeded {len(results) - len(failed)}, failed {len(failed)}: "
          + ", ".join(f"{cid}={kind}" for cid, kind in sorted(failed.items())))

    # Resubmit by custom_id: oversized -> chunked; transient/expired -> unchanged.
    resubmit = []
    for cid, kind in failed.items():
        doc = docs[cid]
        if kind == "invalid_request_error" and len(doc["text"]) > MAX_DOC_CHARS:
            parts = chunk(doc)
            print(f"  {cid}: {len(doc['text']):,} chars > {MAX_DOC_CHARS:,} -> {len(parts)} chunks")
            resubmit += parts
        elif kind == "invalid_request_error":
            print(f"  {cid}: invalid request, not size-related -> human review (not resubmitted)")
        else:
            resubmit.append(doc)
    pass1_hours = (time.time() - started) / 3600

    validation_failures, merged = [], defaultdict(list)
    if resubmit:
        print(f"Pass 2: resubmitting {len(resubmit)} requests "
              f"({', '.join(r['id'] for r in resubmit)})")
        for cid, (kind, data) in submit_and_collect(to_requests(resubmit), live, {}).items():
            if kind != "succeeded":
                print(f"  {cid} failed again ({kind}) -> human review")
            elif cid.split("-part")[0] != cid:
                merged[cid.split("-part")[0]].append(data)
        for parent, parts in merged.items():
            if all(parts):
                print(f"  {parent}: merged {len(parts)} chunk extractions, "
                      f"{len(merge_parts(parts)['line_items'])} line items")
    if live:  # a batch request can't hold a multi-turn retry, so failures go to extract()
        validation_failures = [cid for cid, (k, d) in results.items()
                               if k == "succeeded" and (d is None or validate(d))]
        print(f"  {len(validation_failures)} batch extractions failed validation "
              "-> retry synchronously with extract()")

    # SLA check: each batch pass can take up to 24h; that is what you plan against.
    worst_two_passes = 2 * BATCH_MAX_HOURS
    worst_with_sync = BATCH_MAX_HOURS + len(resubmit) * 30 / 3600  # ~30s per sync call
    print(f"\nSLA check (SLA = {sla_hours}h):")
    print(f"  observed: pass 1 {pass1_hours:.2f}h, total {(time.time() - started) / 3600:.2f}h")
    print(f"  worst case, two batch passes:          {worst_two_passes}h "
          f"-> {'OK' if worst_two_passes <= sla_hours else 'MISSES SLA'}")
    print(f"  worst case, batch + sync resubmission: {worst_with_sync:.1f}h "
          f"-> {'OK' if worst_with_sync <= sla_hours else 'MISSES SLA'}")
    if worst_two_passes > sla_hours:
        print(f"  => submit at least {worst_two_passes - sla_hours:.0f}h earlier, or retry "
              "failures with synchronous calls instead of a second batch")


# ---------------------------------------------------------------- CLI


def main(argv: list[str]) -> None:
    if argv and argv[0] == "batch":
        sla = float(argv[argv.index("--sla-hours") + 1]) if "--sla-hours" in argv else 30
        run_batch(live="--live" in argv, sla_hours=sla)
        return
    args = [a for a in argv if a != "extract"]
    few_shot = "--no-few-shot" not in args
    ids = [a for a in args if not a.startswith("--")]
    docs = [d for d in SAMPLES if not ids or d["id"] in ids]
    if not docs:
        sys.exit(f"unknown doc id; choose from {[d['id'] for d in SAMPLES]}")
    print(f"Extracting {len(docs)} documents (few-shot {'on' if few_shot else 'off'})")
    report([extract(d, few_shot) for d in docs])


if __name__ == "__main__":
    main(sys.argv[1:])
