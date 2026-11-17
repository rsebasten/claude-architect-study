#!/usr/bin/env python3
"""Figure 4 agent loop with two fake tools: get_weather and get_time.

Setup:
    uv python install 3.12 --default   # python3 -> Python 3.12 (~/.local/bin)
    uv pip install --system --break-system-packages --python 3.12 "anthropic==0.125.0" claude-agent-sdk

Auth: no API key needed. If ANTHROPIC_API_KEY is unset, the client reuses
the same gateway + credentials as your Claude Code CLI (base URL, custom
headers, and the token minted by `apiKeyHelper` in ~/.claude/settings.json).

Run:
    python3 support_agent/loop.py
    python3 support_agent/loop.py "What time is it in Paris, and is it raining there?"

Every turn prints its stop_reason, so you can watch the loop go
tool_use -> tool_use -> ... -> end_turn.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import anthropic
import httpx


# --- Client: reuse Claude Code's gateway + auth ----------------------------

def _claude_code_client() -> tuple:
    """Build a client from ~/.claude/settings.json, the way Claude Code does.

    Returns (client, using_gateway).
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic(), False

    settings = json.loads((Path.home() / ".claude" / "settings.json").read_text())
    env = {**settings.get("env", {}), **os.environ}  # real env vars win

    helper = settings.get("apiKeyHelper")
    if not helper:
        sys.exit("No ANTHROPIC_API_KEY and no apiKeyHelper in ~/.claude/settings.json")
    # Same command Claude Code runs to get its token (e.g. `devbar auth claude`).
    token = subprocess.run(helper, shell=True, capture_output=True,
                           text=True, check=True).stdout.strip()

    headers = {}
    for line in env.get("ANTHROPIC_CUSTOM_HEADERS", "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()
    headers["Authorization"] = f"Bearer {token}"  # gateways vary; send both forms

    # Trust the same extra CA bundle Node/Claude Code is configured with.
    verify = env.get("NODE_EXTRA_CA_CERTS") or True
    if env.get("NODE_TLS_REJECT_UNAUTHORIZED") == "0":
        verify = False

    client = anthropic.Anthropic(
        api_key=token,
        base_url=env["ANTHROPIC_BASE_URL"],
        default_headers=headers,
        http_client=httpx.Client(verify=verify),
    )
    return client, True


client, USING_GATEWAY = _claude_code_client()

# Override with e.g. MODEL=us.anthropic.claude-opus-5-5 if your gateway wants
# Bedrock-style IDs.
MODEL = os.environ.get("MODEL", "claude-opus-5-5")

SYSTEM = """You are a concise assistant. Use get_weather and get_time to answer
questions about a city's current weather or local time. If one question needs
several lookups, request them all in a single turn. Never make up a value that
the tools did not return."""

TOOLS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city. Returns temperature in °C and conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Paris'"},
            },
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "get_time",
        "description": "Get the current local time for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Tokyo'"},
            },
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


# --- Fake tools ------------------------------------------------------------
# Hard-coded data in place of real APIs. An unknown city returns an error
# result, so you can also see is_error=True in use.

FAKE_WEATHER = {
    "paris": {"temp_c": 11, "conditions": "light rain"},
    "tokyo": {"temp_c": 16, "conditions": "clear"},
    "new york": {"temp_c": 7, "conditions": "overcast"},
}

FAKE_TIME = {
    "paris": "18:42 CET",
    "tokyo": "02:42 JST (next day)",
    "new york": "12:42 EST",
}


@dataclass
class ToolOutput:
    text: str
    is_error: bool = False


# Cities whose weather lookup raises once (simulated upstream timeout), then
# succeeds on retry. dispatch() turns the exception into is_error=True.
FLAKY_WEATHER = {"london"}
FAKE_WEATHER["london"] = {"temp_c": 9, "conditions": "drizzle"}
FAKE_TIME["london"] = "17:42 GMT"


def get_weather(city: str) -> ToolOutput:
    key = city.strip().lower()
    if key in FLAKY_WEATHER:
        FLAKY_WEATHER.discard(key)  # fail only the first time
        raise TimeoutError("weather service timed out after 5s (transient; retry may succeed)")
    data = FAKE_WEATHER.get(key)
    if data is None:
        return ToolOutput(f"No weather data for '{city}'.", is_error=True)
    return ToolOutput(json.dumps({"city": city, **data}))


def get_time(city: str) -> ToolOutput:
    t = FAKE_TIME.get(city.strip().lower())
    if t is None:
        return ToolOutput(f"No time zone data for '{city}'.", is_error=True)
    return ToolOutput(json.dumps({"city": city, "local_time": t}))


HANDLERS = {"get_weather": get_weather, "get_time": get_time}


def dispatch(name: str, args: dict) -> ToolOutput:
    """YOUR code runs the tool. Failures go back to Claude as is_error results."""
    handler = HANDLERS.get(name)
    if handler is None:
        return ToolOutput(f"Unknown tool: {name}", is_error=True)
    try:
        return handler(**args)
    except Exception as exc:  # report the failure to Claude; don't crash the loop
        return ToolOutput(f"{name} failed: {exc}", is_error=True)


# --- Helpers used by the loop ---------------------------------------------

class TruncatedOutput(Exception):
    def __init__(self, turn: int):
        super().__init__(f"Response hit max_tokens on turn {turn}")
        self.turn = turn


def final_text(resp) -> str:
    return "".join(b.text for b in resp.content if b.type == "text")


def escalate(reason: str, messages: list) -> str:
    """Fail safe, not fail silent: hand off to a human."""
    print(f"[escalate] {reason} ({len(messages)} messages in transcript)", file=sys.stderr)
    return f"ESCALATED: {reason}"


# --- The loop from Figure 4 -----------------------------------------------

def run_agent(user_msg: str, max_turns: int = 15) -> str:
    messages = [{"role": "user", "content": user_msg}]
    for turn in range(max_turns):                    # safety limit, not the exit condition
        kwargs = dict(model=MODEL, max_tokens=2048,
                      system=SYSTEM, tools=TOOLS, messages=messages)
        if USING_GATEWAY:
            resp = client.messages.create(**kwargs)
        else:
            resp = client.beta.messages.create(
                **kwargs,
                # Retries on another model if a safety classifier declines.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        print(f"turn {turn}: stop_reason={resp.stop_reason}")
        messages.append({"role": "assistant", "content": resp.content})  # keep tool_use blocks!

        if resp.stop_reason == "end_turn":           # Claude is done -> exit
            return final_text(resp)
        if resp.stop_reason == "tool_use":
            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    out = dispatch(block.name, block.input)  # YOUR code runs the tool
                    print(f"  -> {block.name}({json.dumps(block.input)}) "
                          f"is_error={out.is_error}: {out.text}")
                    results.append({"type": "tool_result",
                                    "tool_use_id": block.id,  # must match the request
                                    "content": out.text,
                                    "is_error": out.is_error})
            messages.append({"role": "user", "content": results})  # all results, one message
            continue
        if resp.stop_reason == "max_tokens":
            raise TruncatedOutput(turn)              # handle explicitly, never ignore
        # Any other stop reason (e.g. refusal) is also handled, not ignored.
        return escalate(f"unexpected stop_reason: {resp.stop_reason}", messages)
    return escalate("turn budget exhausted", messages)  # fail safe, not fail silent


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "What's the weather and local time in Paris and Tokyo? Also check Atlantis."
    )
    print(f"user: {question}\n")
    print("\nfinal:", run_agent(question))
