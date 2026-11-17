"""Unit tests for bookings_api. Matches `.claude/rules/tests.md` (test_*.py)."""

import unittest

import bookings_api as api


class GetBookingHandlerTest(unittest.TestCase):
    def test_returns_booking_when_ref_and_name_match(self):
        result = api.get_booking_handler({"ref": "abc123", "last_name": "NGUYEN"})
        self.assertEqual(result["flight"], "SA101")

    def test_validation_error_for_malformed_ref(self):
        result = api.get_booking_handler({"ref": "AB-1", "last_name": "Nguyen"})
        self.assertEqual(result["errorCategory"], "validation")
        self.assertFalse(result["isRetryable"])

    def test_not_found_when_last_name_differs(self):
        result = api.get_booking_handler({"ref": "ABC123", "last_name": "Patel"})
        self.assertEqual(result["errorCategory"], "not_found")
        self.assertFalse(result["isRetryable"])

    def test_only_transient_is_retryable(self):
        self.assertTrue(api.error("transient", "timeout")["isRetryable"])


if __name__ == "__main__":
    unittest.main()
