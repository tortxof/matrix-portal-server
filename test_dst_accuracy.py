#!/usr/bin/env python3
"""Test DST transition accuracy to the second with various second values"""

import datetime
import unittest
from zoneinfo import ZoneInfo

from app import get_next_dst_transition


class TestDSTAccuracy(unittest.TestCase):
    """Test DST transition detection with second-level accuracy"""

    def test_us_spring_forward_36min_before(self):
        """US Spring forward 2024 - 36 minutes 15 seconds before transition"""
        test_time = datetime.datetime(
            2024, 3, 10, 1, 23, 45, tzinfo=ZoneInfo("America/New_York")
        )
        expected = datetime.datetime(
            2024, 3, 10, 2, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("America/New_York"), test_time
        )

        self.assertIsNotNone(next_dst_change, "Should find transition")
        expected_timestamp = int(expected.timestamp())
        self.assertLessEqual(
            abs(next_dst_change - expected_timestamp),
            1,
            "Should be accurate within 1 second",
        )
        self.assertEqual(new_utc_offset, -14400, "New offset should be EDT (UTC-4)")

    def test_us_spring_forward_12min_before(self):
        """US Spring forward 2024 - 12 minutes 27 seconds before transition"""
        test_time = datetime.datetime(
            2024, 3, 10, 1, 47, 33, tzinfo=ZoneInfo("America/New_York")
        )
        expected = datetime.datetime(
            2024, 3, 10, 2, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("America/New_York"), test_time
        )

        self.assertIsNotNone(next_dst_change)
        expected_timestamp = int(expected.timestamp())
        self.assertLessEqual(abs(next_dst_change - expected_timestamp), 1)
        self.assertEqual(new_utc_offset, -14400, "New offset should be EDT (UTC-4)")

    def test_us_fall_back(self):
        """US Fall back 2024 - 44 minutes 18 seconds before transition"""
        test_time = datetime.datetime(
            2024, 11, 3, 1, 15, 42, tzinfo=ZoneInfo("America/New_York")
        )
        expected_utc = datetime.datetime(2024, 11, 3, 6, 0, 0, tzinfo=ZoneInfo("UTC"))
        expected = expected_utc.astimezone(ZoneInfo("America/New_York"))

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("America/New_York"), test_time
        )

        self.assertIsNotNone(next_dst_change)
        expected_timestamp = int(expected.timestamp())
        self.assertLessEqual(abs(next_dst_change - expected_timestamp), 1)
        self.assertEqual(new_utc_offset, -18000, "New offset should be EST (UTC-5)")

    def test_europe_spring_forward(self):
        """Europe/London Spring forward 2024 - 22 minutes 31 seconds before"""
        test_time = datetime.datetime(
            2024, 3, 31, 0, 37, 29, tzinfo=ZoneInfo("Europe/London")
        )
        expected = datetime.datetime(
            2024, 3, 31, 1, 0, 0, tzinfo=ZoneInfo("Europe/London")
        )

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("Europe/London"), test_time
        )

        self.assertIsNotNone(next_dst_change)
        expected_timestamp = int(expected.timestamp())
        self.assertLessEqual(abs(next_dst_change - expected_timestamp), 1)
        self.assertEqual(new_utc_offset, 3600, "New offset should be BST (UTC+1)")

    def test_australia_fall_back(self):
        """Australia/Sydney Fall back 2025 - 51 minutes 43 seconds before"""
        test_time = datetime.datetime(
            2025, 4, 6, 2, 8, 17, tzinfo=ZoneInfo("Australia/Sydney")
        )
        expected_utc = datetime.datetime(2025, 4, 5, 16, 0, 0, tzinfo=ZoneInfo("UTC"))
        expected = expected_utc.astimezone(ZoneInfo("Australia/Sydney"))

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("Australia/Sydney"), test_time
        )

        self.assertIsNotNone(next_dst_change)
        expected_timestamp = int(expected.timestamp())
        self.assertLessEqual(abs(next_dst_change - expected_timestamp), 1)
        self.assertEqual(new_utc_offset, 36000, "New offset should be AEST (UTC+10)")

    def test_no_transition_current_time(self):
        """No transition in next 2 hours - current time (November 2025)"""
        test_time = datetime.datetime(
            2025, 11, 9, 14, 32, 18, tzinfo=ZoneInfo("America/New_York")
        )

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("America/New_York"), test_time
        )

        self.assertIsNone(next_dst_change)
        self.assertIsNone(new_utc_offset)

    def test_no_dst_timezone(self):
        """Timezone without DST (America/Phoenix)"""
        test_time = datetime.datetime(
            2024, 3, 10, 1, 45, 30, tzinfo=ZoneInfo("America/Phoenix")
        )

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("America/Phoenix"), test_time
        )

        self.assertIsNone(next_dst_change)
        self.assertIsNone(new_utc_offset)

    def test_transition_outside_2hour_window(self):
        """Transition just outside 2-hour window - should return None"""
        test_time = datetime.datetime(
            2024, 3, 9, 23, 54, 55, tzinfo=ZoneInfo("America/New_York")
        )

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("America/New_York"), test_time
        )

        self.assertIsNone(next_dst_change)
        self.assertIsNone(new_utc_offset)

    def test_transition_inside_2hour_window(self):
        """Transition just inside 2-hour window - should find it"""
        test_time = datetime.datetime(
            2024, 3, 10, 0, 0, 37, tzinfo=ZoneInfo("America/New_York")
        )
        expected = datetime.datetime(
            2024, 3, 10, 2, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )

        next_dst_change, new_utc_offset = get_next_dst_transition(
            ZoneInfo("America/New_York"), test_time
        )

        self.assertIsNotNone(next_dst_change)
        expected_timestamp = int(expected.timestamp())
        self.assertLessEqual(abs(next_dst_change - expected_timestamp), 1)
        self.assertEqual(new_utc_offset, -14400, "New offset should be EDT (UTC-4)")


if __name__ == "__main__":
    unittest.main()
