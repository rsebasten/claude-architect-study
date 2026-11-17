#!/usr/bin/env python3
"""Exercise 4: multi-agent research pipeline (Agent SDK).

- Coordinator gets only the Task tool and three subagents (AgentDefinition):
  web_researcher, doc_analyst (parallel), then synthesizer. Subagents do NOT
  inherit the coordinator's context, so every Task prompt must carry it explicitly.
- Subagents return structured JSON: findings[{claim, evidence_excerpt, source_url,
  source_name, publication_date}] plus status / error / coverage_note.
- --timeout: reading one document times out; doc_analyst returns status "partial"
  with structured error context and the coordinator carries on with partial results.
- Conflicting figures (41% vs 34%, $18 vs $21) must survive synthesis with attribution;
  established vs contested findings are reported separately.
- PreToolUse hooks: deny unknown subagent types, deny the coordinator calling the
  research tools itself, and log each Task prompt to check context was passed.

Run:
    python3 research/research_agent.py               # parallel, no failures
    python3 research/research_agent.py --timeout     # simulated subagent timeout
    python3 research/research_agent.py --sequential  # one subagent at a time (timing baseline)
"""

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "support_agent"))
from escalation_agent import auth_only_settings, result_text  # noqa: E402

from corpus import DOCUMENTS, TIMEOUT_DOC, WEB_PAGES  # noqa: E402

MODEL = os.environ.get("MODEL", "claude-opus-5-5")
SERVER = "research"
SIMULATE_TIMEOUT = False
FETCH_TIMEOUT_S = 2.0
QUESTION = ("How well is Lumen Bay's curbside composting program performing? "
            "Cover participation, landfill diversion, cost per household and resident satisfaction.")
SUBAGENTS = {"web_researcher", "doc_analyst", "synthesizer"}
REQUIRED_FINDING_KEYS = {"claim", "evidence_excerpt", "source_url", "source_name", "publication_date"}


# --- Tools (fictional corpus) -------------------------------------------------

def ok(payload) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


def error(category: str, retryable: bool, description: str, **context) -> dict:
    body = {"errorCategory": category, "isRetryable": retryable, "description": description, **context}
    return {"content": [{"type": "text", "text": json.dumps(body)}], "is_error": True}


@tool("search_web", "Search public web pages. Returns url, source_name, publication_date and text "
      "for each match. Use short keyword queries such as 'composting participation'.",
      {"query": str})
async def search_web(args: dict) -> dict:
    words = set(re.findall(r"[a-z]+", args["query"].lower()))
    hits = [{k: p[k] for k in ("url", "source_name", "publication_date", "text")}
            for p in WEB_PAGES if words & set(p["keywords"])]
    return ok({"results": hits})


@tool("list_documents", "List internal documents (id, title, publication_date). "
      "Call this first, then read_document for each relevant id.", {})
async def list_documents(args: dict) -> dict:
    return ok([{"doc_id": k, "title": d["title"], "publication_date": d["publication_date"]}
               for k, d in DOCUMENTS.items()])


async def _fetch(doc_id: str) -> dict:
    if SIMULATE_TIMEOUT and doc_id == TIMEOUT_DOC:
        await asyncio.sleep(FETCH_TIMEOUT_S * 3)  # the document store hangs
    return DOCUMENTS[doc_id]


@tool("read_document", "Read one internal document by doc_id (from list_documents). Its source_url "
      "is doc://<doc_id>.", {"doc_id": str})
async def read_document(args: dict) -> dict:
    doc_id = args["doc_id"]
    if doc_id not in DOCUMENTS:
        return error("validation", False, f"Unknown doc_id {doc_id!r}; call list_documents.")
    try:
        doc = await asyncio.wait_for(_fetch(doc_id), FETCH_TIMEOUT_S)
    except TimeoutError:
        return error("timeout", True, f"Document store did not respond within {FETCH_TIMEOUT_S}s.",
                     attempted={"tool": "read_document", "doc_id": doc_id})
    return ok({"source_url": f"doc://{doc_id}", **doc})


TOOLS = [search_web, list_documents, read_document]
TOOL_NAMES = [f"mcp__{SERVER}__{t.name}" for t in TOOLS]


# --- Agents -------------------------------------------------------------------

OUTPUT_CONTRACT = """Your final message must be ONLY this JSON object, no prose, no code fence:
{"status": "ok" | "partial" | "failed",
 "findings": [{"claim": str, "evidence_excerpt": "<verbatim quote from the source>",
               "source_url": str, "source_name": str, "publication_date": "YYYY-MM-DD"}],
 "error": null | {"failure_type": str, "attempted": str, "isRetryable": bool, "detail": str},
 "coverage_note": "<what you could and could not cover>"}
One finding per figure. Quote evidence verbatim. Never invent a source or a figure.
Tool errors are JSON {errorCategory, isRetryable, description}: retry a retryable error once;
if it fails again, keep the findings you already have, set status "partial" and fill "error"."""

AGENTS = {
    "web_researcher": AgentDefinition(
        description="Searches public web pages for a research question and returns cited findings as JSON.",
        prompt="You research public web sources. Run a few targeted searches (one per sub-topic).\n"
               + OUTPUT_CONTRACT,
        tools=[f"mcp__{SERVER}__search_web"],
        model="inherit",
        background=False,  # synchronous: the Task result IS the subagent's output
    ),
    "doc_analyst": AgentDefinition(
        description="Reads internal documents for a research question and returns cited findings as JSON.",
        prompt="You analyse internal documents. List them, read every relevant one, extract figures.\n"
               + OUTPUT_CONTRACT,
        tools=[f"mcp__{SERVER}__list_documents", f"mcp__{SERVER}__read_document"],
        model="inherit",
        background=False,  # synchronous: the Task result IS the subagent's output
    ),
    "synthesizer": AgentDefinition(
        description="Combines findings JSON from other agents into a sourced report. Has no tools.",
        prompt="""You synthesise research findings you are given; you have no tools and no other context.
Write a markdown report with exactly these sections:
## Established - figures stated by 2+ independent sources (list every source).
## Contested - figures where sources disagree. Keep EVERY value, each with source_name,
   source_url and publication_date, and give the likely reason (method, date, scope).
   Do not pick a winner or average values.
## Single-source - figures from only one source.
## Coverage gaps - every error or partial status reported by an agent, and what is missing.
Cite each figure as [source_name](source_url, publication_date). Use only the URLs given to you.""",
        tools=[],
        model="inherit",
        background=False,  # synchronous: the Task result IS the subagent's output
    ),
}


def coordinator_prompt(sequential: bool) -> str:
    launch = ("Launch web_researcher, wait for its result, then launch doc_analyst."
              if sequential else
              "Launch web_researcher AND doc_analyst in the SAME response (two Task calls in one "
              "message) so they run in parallel.")
    return f"""You coordinate a research pipeline. You cannot research yourself; delegate with Task.
Subagents do not see this conversation: every Task prompt must restate the full research
question and the sub-topics to cover.
1. {launch}
2. Then call synthesizer once. Its prompt must contain the research question and BOTH agents'
   JSON outputs verbatim, including any error objects. Do not summarise or drop findings.
3. If an agent fails or returns partial results, do not re-run it; continue with what you have
   and make sure the gap is passed to synthesizer.
4. Your final answer is the synthesizer's report, unchanged."""


# --- Hooks --------------------------------------------------------------------

TASK_LOG: list[dict] = []


def deny(input_data: dict, reason: str) -> dict:
    print(f"  [hook] DENY {input_data['tool_name']}: {reason}")
    return {"hookSpecificOutput": {"hookEventName": input_data["hook_event_name"],
                                   "permissionDecision": "deny", "permissionDecisionReason": reason}}


async def task_hook(input_data, tool_use_id, context):
    ti = input_data["tool_input"]
    agent = ti.get("subagent_type")
    if agent not in SUBAGENTS:
        return deny(input_data, f"Unknown subagent {agent!r}; use one of {sorted(SUBAGENTS)}.")
    prompt = ti.get("prompt", "")
    TASK_LOG.append({"agent": agent, "has_question": "Lumen Bay" in prompt and "compost" in prompt.lower(),
                     "prompt_chars": len(prompt), "asked_background": bool(ti.get("run_in_background"))})
    if ti.get("run_in_background"):
        # The model can request async mode per call, overriding AgentDefinition(background=False).
        # Force it off deterministically so the Task result is the subagent's JSON.
        print(f"  [hook] {agent}: run_in_background=true -> forced synchronous")
        return {"hookSpecificOutput": {"hookEventName": input_data["hook_event_name"],
                                       "permissionDecision": "allow",
                                       "updatedInput": {**ti, "run_in_background": False}}}
    return {}


async def coordinator_cannot_research(input_data, tool_use_id, context):
    if not input_data.get("agent_id"):  # only set when a subagent makes the call
        return deny(input_data, "The coordinator must delegate research to a subagent.")
    return {}


# --- Run + checks -------------------------------------------------------------

def parse_json(text: str):
    start, end = text.find("{"), text.rfind("}")
    try:
        return json.loads(text[start:end + 1])
    except (ValueError, json.JSONDecodeError):
        return None


async def run(sequential: bool) -> None:
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=coordinator_prompt(sequential),
        tools=["Task"],                        # only built-in tool: delegation
        allowed_tools=["Task", *TOOL_NAMES],   # MCP tools pre-approved for the subagents
        agents=AGENTS,
        mcp_servers={SERVER: create_sdk_mcp_server(name=SERVER, version="1.0.0", tools=TOOLS)},
        hooks={"PreToolUse": [
            HookMatcher(matcher="Task|Agent", hooks=[task_hook]),
            HookMatcher(matcher=f"mcp__{SERVER}__.*", hooks=[coordinator_cannot_research]),
        ]},
        max_turns=12,                          # safety limit; the SDK exits on stop_reason
        setting_sources=[],
        settings=auth_only_settings(),
    )

    tasks: dict[str, dict] = {}   # Task tool_use_id -> {agent, start, end, output}
    batches: dict[str, int] = {}  # coordinator message_id -> Task calls (SDK splits blocks into messages)
    final = None
    t0 = time.monotonic()
    async for msg in query(prompt=QUESTION, options=options):
        now = time.monotonic() - t0
        if isinstance(msg, AssistantMessage):
            who = "coordinator" if msg.parent_tool_use_id is None else \
                tasks.get(msg.parent_tool_use_id, {}).get("agent", "subagent")
            calls = [b for b in msg.content if isinstance(b, ToolUseBlock)]
            spawned = [b for b in calls if b.name in ("Task", "Agent")]
            if msg.parent_tool_use_id is None and spawned:
                batches[msg.message_id] = batches.get(msg.message_id, 0) + len(spawned)
            for b in calls:
                if b in spawned:
                    tasks[b.id] = {"agent": b.input.get("subagent_type"), "start": now}
                    print(f"{now:6.1f}s {who} -> Task({b.input.get('subagent_type')})")
                else:
                    print(f"{now:6.1f}s   {who} -> {b.name.removeprefix(f'mcp__{SERVER}__')}"
                          f"({json.dumps(b.input)})")
        elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
            for b in msg.content:
                if not isinstance(b, ToolResultBlock):
                    continue
                text = result_text(b)
                if b.tool_use_id in tasks:
                    tasks[b.tool_use_id].update(end=now, output=text)
                    print(f"{now:6.1f}s coordinator <- {tasks[b.tool_use_id]['agent']} done: {text[:90]!r}")
                elif b.is_error:
                    print(f"{now:6.1f}s   <- tool error: {text}")
        elif isinstance(msg, ResultMessage):
            final = msg

    if final is None:
        print("No ResultMessage received.")
        return
    print(f"\nresult: subtype={final.subtype} stop_reason={final.stop_reason} turns={final.num_turns} "
          f"cost=${final.total_cost_usd or 0:.4f} wall={final.duration_ms / 1000:.1f}s")
    if final.subtype != "success" or final.stop_reason in ("max_tokens", "refusal"):
        print("Pipeline did not finish cleanly - escalate for human review.")
        return
    report = final.result or ""
    print(f"\n{'=' * 70}\n{report}\n{'=' * 70}")
    check(tasks, batches, report, sequential)


def check(tasks: dict, batches: dict[str, int], report: str, sequential: bool) -> None:
    rows = []
    batches = list(batches.values())
    researchers = [t for t in tasks.values() if t["agent"] in ("web_researcher", "doc_analyst")]
    known_urls = set()
    for t in researchers:
        data = parse_json(t.get("output", ""))
        valid = bool(data) and all(REQUIRED_FINDING_KEYS <= f.keys() for f in data.get("findings", []))
        if data:
            known_urls |= {f["source_url"] for f in data.get("findings", [])}
        err = (data or {}).get("error")
        rows.append((f"{t['agent']} output", f"status={(data or {}).get('status')} "
                     f"findings={len((data or {}).get('findings', []))} schema_ok={valid}"
                     + (f" error={err.get('failure_type')}" if err else "")))
        rows.append((f"{t['agent']} time", f"{t['start']:.1f}s -> {t.get('end', float('nan')):.1f}s"))
    rows.append(("Task calls per coordinator msg", str(batches)
                 + ("" if sequential else "  (parallel)" if any(n >= 2 for n in batches) else "  NOT parallel")))
    rows.append(("Context passed in Task prompts", ", ".join(
        f"{t['agent']}={'yes' if t['has_question'] else 'NO'}({t['prompt_chars']}ch"
        f"{', bg forced off' if t['asked_background'] else ''})" for t in TASK_LOG)))
    cited = set(re.findall(r"(?:https?|doc)://[\w./-]*\w", report))
    rows.append(("Report URLs traced to findings", "all" if cited <= known_urls
                 else f"UNTRACED: {sorted(cited - known_urls)}"))
    rows.append(("Conflict kept (41% and 34%)", str("41%" in report and "34%" in report)))
    rows.append(("Conflict kept ($18 and $21)", str("$18" in report and "$21" in report)))
    rows.append(("Established/Contested split", str("## Established" in report and "## Contested" in report)))
    if SIMULATE_TIMEOUT:
        rows.append(("Timeout surfaced in gaps", str("timeout" in report.lower() or "hauler" in report.lower())))
    print("\nChecks:")
    for k, v in rows:
        print(f"  {k:<34} {v}")


if __name__ == "__main__":
    args = sys.argv[1:]
    SIMULATE_TIMEOUT = "--timeout" in args
    asyncio.run(run(sequential="--sequential" in args))
