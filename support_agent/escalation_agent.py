#!/usr/bin/env python3
"""Exercise 1: multi-tool support agent with structured errors and hook-based escalation.

- Four in-process MCP tools; get_booking and search_bookings are deliberately similar,
  so their descriptions must tell Claude which one to pick.
- Every tool failure is a structured error: {errorCategory, isRetryable, description}.
- A PreToolUse hook blocks issue_refund above REFUND_LIMIT_USD and opens an escalation
  ticket in code - the limit is enforced deterministically, not by the prompt.
- stop_reason is printed for every assistant turn and for the final result.

Setup (Agent SDK needs Python >= 3.10):
    uv python install 3.12 --default   # python3 -> Python 3.12 (~/.local/bin)
    uv pip install --system --break-system-packages --python 3.12 "anthropic==0.125.0" claude-agent-sdk

Run:
    python3 support_agent/escalation_agent.py              # all scenarios
    python3 support_agent/escalation_agent.py large_refund # one scenario
    python3 support_agent/escalation_agent.py "Your own question"
"""

import asyncio
import copy
import json
import math
import os
import sys
from itertools import count
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    StreamEvent,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

MODEL = os.environ.get("MODEL", "claude-opus-5-5")
SERVER = "support"
REFUND_LIMIT_USD = 500
REFUND_TOOL = f"mcp__{SERVER}__issue_refund"

SYSTEM = f"""You are a concise airline customer-support agent.

Identity: before discussing or changing a booking, verify it with get_booking using
the booking reference and the passenger's last name. If the customer has no
reference, use search_bookings with their email.

Tool errors are JSON with errorCategory, isRetryable and description:
- isRetryable true: retry the same call once; if it fails again, tell the customer.
- isRetryable false: do not retry. Explain the problem plainly or ask for corrected details.
- errorCategory "policy": do not work around it.

Refunds: call issue_refund for the amount requested. Refunds totalling more than
${REFUND_LIMIT_USD} per booking are blocked automatically and handed to a human; when that
happens, give the customer the ticket ID and do not promise an outcome.

Call escalate_to_human when the customer asks for a person, or when the request is
outside what your tools can do. Handle every part of a multi-part request, and make
independent lookups in the same turn. Never invent booking details."""


# --- Fictional data ----------------------------------------------------------

BOOKINGS = {
    "ABC123": {"last_name": "Nguyen", "email": "jordan.nguyen@example.com",
               "passenger": "Jordan Nguyen", "itinerary": "SFO → JFK, 2026-12-15 09:00",
               "fare_class": "Flex", "paid_usd": 850, "refundable": True, "refunded_usd": 0},
    "XYZ789": {"last_name": "Patel", "email": "priya.patel@example.com",
               "passenger": "Priya Patel", "itinerary": "LAX → SEA, 2026-11-30 14:10",
               "fare_class": "Flex", "paid_usd": 320, "refundable": True, "refunded_usd": 0},
    "PQR555": {"last_name": "Patel", "email": "priya.patel@example.com",
               "passenger": "Priya Patel", "itinerary": "BOS → DEN, 2027-01-08 07:30",
               "fare_class": "Flex", "paid_usd": 480, "refundable": True, "refunded_usd": 0},
    "DEF456": {"last_name": "Garcia", "email": "maria.garcia@example.com",
               "passenger": "Maria Garcia", "itinerary": "ORD → MIA, 2026-12-02 18:45",
               "fare_class": "Basic", "paid_usd": 210, "refundable": False, "refunded_usd": 0},
}
INITIAL_BOOKINGS = copy.deepcopy(BOOKINGS)
FLAKY_REFS: set[str] = set()  # refs whose first get_booking times out; a retry succeeds
VERIFIED_REFS: set[str] = set()  # refs that passed get_booking in this scenario


def reset_data() -> None:
    """Give every scenario fresh data so earlier refunds don't change later results."""
    BOOKINGS.clear()
    BOOKINGS.update(copy.deepcopy(INITIAL_BOOKINGS))
    FLAKY_REFS.clear()
    FLAKY_REFS.add("XYZ789")
    VERIFIED_REFS.clear()

ESCALATIONS: list[dict] = []
_ticket_ids = count(1001)


def open_ticket(source: str, reason: str, details: dict) -> str:
    ticket_id = f"ESC-{next(_ticket_ids)}"
    ESCALATIONS.append({"ticket_id": ticket_id, "source": source,
                        "reason": reason, **details})
    return ticket_id


# --- Tool result helpers -----------------------------------------------------

def ok(payload: dict) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


def error(category: str, retryable: bool, description: str) -> dict:
    body = {"errorCategory": category, "isRetryable": retryable, "description": description}
    return {"content": [{"type": "text", "text": json.dumps(body)}], "is_error": True}


def public_view(ref: str, b: dict) -> dict:
    return {"booking_reference": ref, "passenger": b["passenger"],
            "itinerary": b["itinerary"], "fare_class": b["fare_class"],
            "paid_usd": b["paid_usd"], "refundable": b["refundable"],
            "refunded_usd": b["refunded_usd"]}


# --- Tools -------------------------------------------------------------------

@tool(
    "get_booking",
    "Retrieve ONE booking when the customer gives a booking reference (6 characters, "
    "e.g. ABC123) AND their last name. This is the identity check required before "
    "discussing or changing a booking. Do not use it to search by email - use "
    "search_bookings for that. Returns itinerary, fare class, amount paid, refund status.",
    {
        "type": "object",
        "properties": {
            "booking_reference": {"type": "string", "description": "6-character booking reference, e.g. ABC123."},
            "last_name": {"type": "string", "description": "Passenger last name as given by the customer."},
        },
        "required": ["booking_reference", "last_name"],
    },
)
async def get_booking(args: dict) -> dict:
    ref = str(args.get("booking_reference", "")).strip().upper()
    last = str(args.get("last_name", "")).strip()
    if len(ref) != 6 or not last:
        return error("validation", False, "A 6-character booking reference and a last name are required.")
    if ref in FLAKY_REFS:
        FLAKY_REFS.discard(ref)
        return error("transient", True, "Booking service timed out after 5s.")
    b = BOOKINGS.get(ref)
    if b is None or b["last_name"].casefold() != last.casefold():
        # Same message for both cases so the tool doesn't leak which part was wrong.
        return error("not_found", False, "No booking matches that reference and last name.")
    VERIFIED_REFS.add(ref)
    return ok(public_view(ref, b))


@tool(
    "search_bookings",
    "Find ALL bookings for a customer by email address, when they do NOT have their "
    "booking reference. Returns a summary list (reference, itinerary). Do not use it "
    "when a reference and last name are available - use get_booking instead.",
    {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "Email address on the booking."},
        },
        "required": ["email"],
    },
)
async def search_bookings(args: dict) -> dict:
    email = str(args.get("email", "")).strip().lower()
    if "@" not in email:
        return error("validation", False, "A valid email address is required.")
    matches = [{"booking_reference": ref, "itinerary": b["itinerary"]}
               for ref, b in BOOKINGS.items() if b["email"] == email]
    if not matches:
        return error("not_found", False, "No bookings found for that email.")
    return ok({"email": email, "bookings": matches})


@tool(
    "issue_refund",
    f"Refund an amount in USD to the original payment method for a verified booking. "
    f"Only refundable fares can be refunded, up to the amount paid minus prior refunds. "
    f"Refunds totalling more than ${REFUND_LIMIT_USD} per booking require human approval and are routed to an "
    f"agent automatically.",
    {
        "type": "object",
        "properties": {
            "booking_reference": {"type": "string", "description": "Verified booking reference."},
            "amount_usd": {"type": "number", "description": "Refund amount in USD, greater than 0."},
            "reason": {"type": "string", "description": "Short reason for the refund, in the customer's words."},
        },
        "required": ["booking_reference", "amount_usd", "reason"],
    },
)
async def issue_refund(args: dict) -> dict:
    ref = str(args.get("booking_reference", "")).strip().upper()
    b = BOOKINGS.get(ref)
    if b is None:
        return error("not_found", False, f"No booking {ref}.")
    if ref not in VERIFIED_REFS:
        # Identity check enforced in code, not just in the system prompt.
        return error("policy", False, "Verify the booking with get_booking (reference + last name) first.")
    try:
        amount = float(args["amount_usd"])
    except (KeyError, TypeError, ValueError):
        return error("validation", False, "amount_usd must be a number.")
    if not math.isfinite(amount) or amount <= 0:
        return error("validation", False, "Refund amount must be a finite number greater than 0.")
    if not b["refundable"]:
        return error("policy", False, f"{b['fare_class']} fares are non-refundable.")
    remaining = b["paid_usd"] - b["refunded_usd"]
    if amount > remaining:
        return error("validation", False, f"Amount exceeds the refundable balance of ${remaining:.2f}.")
    b["refunded_usd"] += amount
    return ok({"booking_reference": ref, "refunded_usd": amount,
               "refundable_balance_usd": remaining - amount, "status": "processed"})


@tool(
    "escalate_to_human",
    "Hand the conversation to a human agent. Use when the customer asks for a person, "
    "or the request is outside what the other tools can do. Include a summary a human "
    "can act on without rereading the conversation.",
    {
        "type": "object",
        "properties": {
            "reason": {"type": "string", "description": "Why a human is needed."},
            "summary": {"type": "string", "description": "What the customer wants and what has been done so far."},
            "booking_reference": {"type": "string", "description": "Booking reference, if known."},
        },
        "required": ["reason", "summary"],
    },
)
async def escalate_to_human(args: dict) -> dict:
    ticket_id = open_ticket("agent", args.get("reason", ""),
                            {"summary": args.get("summary", ""),
                             "booking_reference": args.get("booking_reference")})
    return ok({"ticket_id": ticket_id, "status": "queued_for_human"})


# --- PreToolUse interceptor ---------------------------------------------------

async def refund_limit_hook(input_data, tool_use_id, context):
    args = input_data["tool_input"]
    try:
        amount = float(args.get("amount_usd"))
    except (TypeError, ValueError):
        return {}  # let the tool return its own validation error
    if not math.isfinite(amount) or amount <= 0:
        return {}  # same: the tool rejects it
    # Count earlier refunds on the booking so the limit can't be dodged by splitting.
    booking = BOOKINGS.get(str(args.get("booking_reference", "")).strip().upper())
    total = amount + (booking["refunded_usd"] if booking else 0)
    if total <= REFUND_LIMIT_USD:
        print(f"  [hook] issue_refund ${amount:.2f} (total ${total:.2f}) <= ${REFUND_LIMIT_USD} -> allow")
        return {}

    ticket_id = open_ticket("hook", f"Refunds totalling ${total:.2f} exceed ${REFUND_LIMIT_USD} limit",
                            {"booking_reference": args.get("booking_reference"),
                             "requested_amount_usd": amount,
                             "customer_reason": args.get("reason")})
    print(f"  [hook] issue_refund ${amount:.2f} (total ${total:.2f}) > ${REFUND_LIMIT_USD} -> deny, {ticket_id}")
    reason = json.dumps({
        "errorCategory": "policy", "isRetryable": False,
        "description": (f"Refunds totalling more than ${REFUND_LIMIT_USD} per booking need human approval. "
                        f"Escalation ticket {ticket_id} has been opened; do not retry "
                        f"or split the refund into smaller amounts."),
        "ticket_id": ticket_id,
    })
    return {"hookSpecificOutput": {
        "hookEventName": input_data["hook_event_name"],
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}


# --- Run ---------------------------------------------------------------------

SCENARIOS = {
    "small_refund": "Booking ABC123, last name Nguyen. My seat upgrade didn't work - please refund the $120.",
    "large_refund": "Booking ABC123, last name Nguyen. My flight was cancelled, refund the full $850 fare.",
    "email_lookup": "I lost my booking reference. My email is priya.patel@example.com - which flights do I have?",
    "retryable": "Can you check booking XYZ789 for Patel? When does it leave?",
    "multi_aspect": ("Two things: look up ABC123 (Nguyen) and refund $40 for a missed meal. "
                     "Also check DEF456 for Garcia - can I get a refund on that one, and "
                     "what about booking QQQ000 for Lee?"),
    "wants_human": "This is the third time I'm writing about ABC123 (Nguyen). I want to talk to a real person.",
}


def result_text(block: ToolResultBlock) -> str:
    if isinstance(block.content, list):
        return "".join(c.get("text", "") for c in block.content)
    return block.content or ""


def auth_only_settings() -> str | None:
    """Pass through only the gateway login from ~/.claude/settings.json."""
    path = Path.home() / ".claude" / "settings.json"
    if not path.exists():
        return None
    user = json.loads(path.read_text())
    return json.dumps({k: user[k] for k in ("apiKeyHelper", "env") if k in user})


async def run_agent(question: str) -> None:
    tools = [get_booking, search_bookings, issue_refund, escalate_to_human]
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM,
        tools=[],  # no built-in Bash/Read/Edit tools
        mcp_servers={SERVER: create_sdk_mcp_server(name=SERVER, version="1.0.0", tools=tools)},
        allowed_tools=[f"mcp__{SERVER}__{t.name}" for t in tools],
        hooks={"PreToolUse": [HookMatcher(matcher=REFUND_TOOL, hooks=[refund_limit_hook])]},
        max_turns=15,  # safety limit; the SDK exits on stop_reason
        include_partial_messages=True,  # raw API stream events carry each turn's stop_reason
        setting_sources=[],  # isolation: no CLAUDE.md, hooks or plugins from settings files
        settings=auth_only_settings(),
    )

    tool_names: dict[str, str] = {}
    turn = 0
    async for msg in query(prompt=question, options=options):
        if isinstance(msg, StreamEvent):
            if msg.event.get("type") == "message_delta":
                turn += 1
                print(f"  turn {turn}: stop_reason={msg.event['delta'].get('stop_reason')}")
        elif isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, ToolUseBlock):
                    tool_names[b.id] = b.name
                    print(f"  -> {b.name.removeprefix(f'mcp__{SERVER}__')}({json.dumps(b.input)})")
        elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
            for b in msg.content:
                if isinstance(b, ToolResultBlock):
                    name = tool_names.get(b.tool_use_id, "?").removeprefix(f"mcp__{SERVER}__")
                    print(f"  <- {name} is_error={bool(b.is_error)}: {result_text(b)}")
        elif isinstance(msg, ResultMessage):
            print(f"\nresult: subtype={msg.subtype} stop_reason={msg.stop_reason} "
                  f"turns={msg.num_turns} cost=${msg.total_cost_usd or 0:.4f}")
            if msg.subtype != "success" or msg.stop_reason in ("max_tokens", "refusal"):
                ticket_id = open_ticket("runtime", f"Agent did not finish: {msg.subtype}/{msg.stop_reason}",
                                        {"question": question})
                print(f"escalated: {ticket_id} (fail safe, not fail silent)")
            else:
                print(f"\nfinal: {msg.result}")


async def main(args: list[str]) -> None:
    if not args:
        runs = list(SCENARIOS.items())
    elif len(args) == 1 and args[0] in SCENARIOS:
        runs = [(args[0], SCENARIOS[args[0]])]
    else:
        runs = [("custom", " ".join(args))]

    for name, question in runs:
        print(f"\n{'=' * 70}\n[{name}] {question}\n{'=' * 70}")
        reset_data()
        await run_agent(question)

    print(f"\n{'=' * 70}\nEscalation queue ({len(ESCALATIONS)}):")
    for t in ESCALATIONS:
        print("  " + json.dumps(t))


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
