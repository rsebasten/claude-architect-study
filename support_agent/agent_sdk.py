#!/usr/bin/env python3
"""loop.py ported to the Claude Agent SDK, plus a PreToolUse hook that denies get_time.

What changed vs. loop.py:
  - No hand-written `for turn in range(...)` loop and no `messages.create(**kwargs)`:
    the SDK (Claude Code as a library) runs model -> tool -> model for us.
  - get_weather / get_time are in-process MCP tools (@tool + create_sdk_mcp_server).
    Claude sees them as mcp__support__get_weather and mcp__support__get_time.
  - A PreToolUse hook runs before every tool call and denies get_time with a reason.
    Claude receives that reason as an is_error tool_result, and so do we in the
    transcript - the script prints it from the message stream and from the
    on-disk session transcript (JSONL).

Setup (Agent SDK needs Python >= 3.10):
    uv python install 3.12 --default   # python3 -> Python 3.12 (~/.local/bin)
    uv pip install --system --break-system-packages --python 3.12 "anthropic==0.125.0" claude-agent-sdk

Auth: none in code. The SDK launches the Claude Code CLI, which loads
~/.claude/settings.json (gateway, apiKeyHelper) exactly like `claude` does.

Run:
    python3 support_agent/agent_sdk.py
    python3 support_agent/agent_sdk.py "What time is it in Tokyo?"
"""

import asyncio
import json
import os
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

MODEL = os.environ.get("MODEL", "claude-opus-5-5")
SERVER = "support"                       # MCP server key -> tool names mcp__support__*
DENIED_TOOL = f"mcp__{SERVER}__get_time"
DENY_REASON = (
    "get_time is disabled by policy in this demo. Tell the user local time "
    "is unavailable; do not guess it."
)

SYSTEM = """You are a concise assistant. Use get_weather and get_time to answer
questions about a city's current weather or local time. If one question needs
several lookups, request them all in a single turn. Never make up a value that
the tools did not return."""


# --- Fake tools (same data and behaviour as loop.py) -----------------------

FAKE_WEATHER = {
    "paris": {"temp_c": 11, "conditions": "light rain"},
    "tokyo": {"temp_c": 16, "conditions": "clear"},
    "new york": {"temp_c": 7, "conditions": "overcast"},
    "london": {"temp_c": 9, "conditions": "drizzle"},
}
FAKE_TIME = {
    "paris": "18:42 CET",
    "tokyo": "02:42 JST (next day)",
    "new york": "12:42 EST",
    "london": "17:42 GMT",
}
FLAKY_WEATHER = {"london"}  # first lookup times out, retry succeeds


def _text(s: str, is_error: bool = False) -> dict:
    """MCP tool result shape. is_error=True is the SDK's equivalent of loop.py's is_error."""
    return {"content": [{"type": "text", "text": s}], "is_error": is_error}


@tool("get_weather",
      "Get the current weather for a city. Returns temperature in °C and conditions.",
      {"city": str})
async def get_weather(args: dict) -> dict:
    city = args["city"]
    key = city.strip().lower()
    if key in FLAKY_WEATHER:
        FLAKY_WEATHER.discard(key)
        return _text("get_weather failed: weather service timed out after 5s "
                     "(transient; retry may succeed)", is_error=True)
    data = FAKE_WEATHER.get(key)
    if data is None:
        return _text(f"No weather data for '{city}'.", is_error=True)
    return _text(json.dumps({"city": city, **data}))


@tool("get_time", "Get the current local time for a city.", {"city": str})
async def get_time(args: dict) -> dict:
    # Never runs while the hook below denies it - kept so the port is complete.
    city = args["city"]
    t = FAKE_TIME.get(city.strip().lower())
    if t is None:
        return _text(f"No time zone data for '{city}'.", is_error=True)
    return _text(json.dumps({"city": city, "local_time": t}))


# --- PreToolUse hook: deny one tool ---------------------------------------

transcript_paths: set[str] = set()  # hook input tells us where the session JSONL lives


async def deny_get_time(input_data, tool_use_id, context):
    transcript_paths.add(input_data["transcript_path"])
    print(f"  [hook] PreToolUse {input_data['tool_name']}"
          f"({json.dumps(input_data['tool_input'])}) -> deny")
    return {
        "hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],   # "PreToolUse"
            "permissionDecision": "deny",
            "permissionDecisionReason": DENY_REASON,           # what Claude is told
        }
    }


# --- Run -------------------------------------------------------------------

def _result_text(block: ToolResultBlock) -> str:
    if isinstance(block.content, list):
        return "".join(c.get("text", "") for c in block.content)
    return block.content or ""


def denial_reasons_from_jsonl(path: str, denied_ids: set[str]) -> dict[str, str]:
    """Find the tool_result entries for denied calls in the on-disk transcript.

    The JSONL can record the same tool_result more than once, so key by tool_use_id.
    """
    reasons = {}
    with open(path) as f:
        for line in f:
            entry = json.loads(line)
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in denied_ids:
                    body = c.get("content")
                    if isinstance(body, list):
                        body = "".join(x.get("text", "") for x in body)
                    reasons[c["tool_use_id"]] = body
    return reasons


async def run_agent(question: str) -> None:
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM,
        tools=[],                                   # no built-in Bash/Read/Edit/... tools
        mcp_servers={SERVER: create_sdk_mcp_server(
            name=SERVER, version="1.0.0", tools=[get_weather, get_time])},
        allowed_tools=[f"mcp__{SERVER}__get_weather", DENIED_TOOL],  # no permission prompts
        hooks={"PreToolUse": [HookMatcher(matcher=DENIED_TOOL, hooks=[deny_get_time])]},
        max_turns=15,                               # safety limit, like loop.py
    )

    tool_names: dict[str, str] = {}   # tool_use_id -> tool name
    denied_ids: set[str] = set()

    async for msg in query(prompt=question, options=options):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, ToolUseBlock):
                    tool_names[b.id] = b.name
                    print(f"  -> {b.name}({json.dumps(b.input)})")
        elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
            # Tool results come back to Claude as a user turn - same as loop.py.
            for b in msg.content:
                if isinstance(b, ToolResultBlock):
                    name = tool_names.get(b.tool_use_id, "?")
                    print(f"  <- {name} is_error={bool(b.is_error)}: {_result_text(b)}")
                    if name == DENIED_TOOL:
                        denied_ids.add(b.tool_use_id)
        elif isinstance(msg, ResultMessage):
            print(f"\nresult: subtype={msg.subtype} turns={msg.num_turns} "
                  f"cost=${msg.total_cost_usd or 0:.4f}")
            print("\nfinal:", msg.result)
            if msg.permission_denials:
                print("\npermission_denials:", json.dumps(msg.permission_denials, indent=2))

    # The denial reason as recorded in the session transcript on disk.
    for path in transcript_paths:
        print(f"\ntranscript: {path}")
        for tid, reason in denial_reasons_from_jsonl(path, denied_ids).items():
            print(f"  {tid}: {reason}")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or (
        "What's the weather and local time in Paris and Tokyo? Also check Atlantis."
    )
    print(f"user: {q}\n")
    asyncio.run(run_agent(q))
