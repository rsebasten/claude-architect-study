"""Thin API handlers over fictional booking data.

Exists so `.claude/rules/api.md` (paths: src/api/**/*) has a file to match.
Errors follow the shared shape {errorCategory, isRetryable, description}.
"""

import re

BOOKINGS = {
    "ABC123": {"last_name": "Nguyen", "flight": "SA101", "fare_usd": 850},
    "XYZ789": {"last_name": "Patel", "flight": "SA202", "fare_usd": 420},
}

REF_PATTERN = re.compile(r"^[A-Z0-9]{6}$")


def error(category: str, description: str) -> dict:
    return {
        "errorCategory": category,
        "isRetryable": category == "transient",
        "description": description,
    }


def find_booking(ref: str, last_name: str) -> dict | None:
    """Business rule: a booking matches only if reference and last name both match."""
    booking = BOOKINGS.get(ref.upper())
    if booking and booking["last_name"].lower() == last_name.lower():
        return {"ref": ref.upper(), **booking}
    return None


def get_booking_handler(params: dict) -> dict:
    ref = str(params.get("ref", "")).strip()
    last_name = str(params.get("last_name", "")).strip()
    if not REF_PATTERN.match(ref.upper()):
        return error("validation", "ref must be 6 letters or digits, e.g. ABC123.")
    if not last_name:
        return error("validation", "last_name is required.")
    booking = find_booking(ref, last_name)
    if booking is None:
        return error("not_found", f"No booking {ref.upper()} for that last name.")
    return booking
