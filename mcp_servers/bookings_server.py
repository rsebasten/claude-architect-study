#!/usr/bin/env python3
"""Fictional airline bookings exposed as a stdio MCP server for Claude Code.

Registered in the project's .mcp.json, so anyone who opens this folder in Claude Code
gets the tools as mcp__bookings__get_booking and mcp__bookings__search_bookings.
Read-only: refunds stay in escalation_agent.py, where a hook enforces the limit.

Uses mcp 2.x (MCPServer, formerly FastMCP). Test it standalone:
    python3 mcp_servers/bookings_server.py --list
"""

import json
import os
import sys

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

BOOKINGS = {
    "ABC123": {"last_name": "Nguyen", "email": "jordan.nguyen@example.com",
               "itinerary": "SFO → JFK, 2026-12-15 09:00", "fare_class": "Flex", "paid_usd": 850},
    "XYZ789": {"last_name": "Patel", "email": "priya.patel@example.com",
               "itinerary": "LAX → SEA, 2026-11-30 14:10", "fare_class": "Flex", "paid_usd": 320},
    "PQR555": {"last_name": "Patel", "email": "priya.patel@example.com",
               "itinerary": "BOS → DEN, 2027-01-08 07:30", "fare_class": "Flex", "paid_usd": 480},
    "DEF456": {"last_name": "Garcia", "email": "maria.garcia@example.com",
               "itinerary": "ORD → MIA, 2026-12-02 18:45", "fare_class": "Basic", "paid_usd": 210},
}

# Set per scope: .mcp.json passes "demo"; a personal override in ~/.claude.json can pass another value.
ENV = os.environ.get("BOOKINGS_ENV", "unset")

server = MCPServer(
    name="bookings",
    instructions=f"Fictional airline booking lookups ({ENV} environment). Read-only.",
)


def fail(category: str, retryable: bool, description: str) -> ToolError:
    """Structured error, same shape as escalation_agent.py; the client sees isError=true."""
    return ToolError(json.dumps({"errorCategory": category, "isRetryable": retryable,
                                 "description": description}))


@server.tool(description=(
    "Retrieve ONE booking from a 6-character booking reference AND the passenger's last "
    "name. Use search_bookings instead when only an email is known."))
def get_booking(booking_reference: str, last_name: str) -> dict:
    ref = booking_reference.strip().upper()
    b = BOOKINGS.get(ref)
    if len(ref) != 6 or not last_name.strip():
        raise fail("validation", False, "A 6-character reference and a last name are required.")
    if b is None or b["last_name"].casefold() != last_name.strip().casefold():
        raise fail("not_found", False, "No booking matches that reference and last name.")
    return {"environment": ENV, "booking_reference": ref,
            **{k: v for k, v in b.items() if k != "email"}}


@server.tool(description=(
    "List ALL bookings for an email address when the customer has no booking reference. "
    "Returns references and itineraries only."))
def search_bookings(email: str) -> dict:
    email = email.strip().lower()
    if "@" not in email:
        raise fail("validation", False, "A valid email address is required.")
    hits = [{"booking_reference": r, "itinerary": b["itinerary"]}
            for r, b in BOOKINGS.items() if b["email"] == email]
    if not hits:
        raise fail("not_found", False, "No bookings found for that email.")
    return {"environment": ENV, "email": email, "bookings": hits}


if __name__ == "__main__":
    if "--list" in sys.argv:
        import asyncio
        for t in asyncio.run(server.list_tools()):
            print(f"{t.name}: {t.description}")
    else:
        server.run("stdio")
