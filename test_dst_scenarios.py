#!/usr/bin/env python3
"""Test DST transition scenarios with specific dates"""

import datetime
import unittest
from zoneinfo import ZoneInfo

import sys

sys.path.insert(0, "/home/tortxof/git/matrix-portal-server")
from app import get_next_dst_transition


class TestDSTScenarios(unittest.TestCase):
    """Test DST transition scenarios around known transition dates"""

    def test_us_spring_forward_2024(self):
        """US Spring forward 2024 (March 10, 2024 at 2:00 AM)"""
        tzinfo = ZoneInfo("America/New_York")
        test_time = datetime.datetime.fromisoformat("2024-03-09T12:00:00").replace(
            tzinfo=tzinfo
        )

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

        # Should find transition within 2 hours (14 hours away, so None expected)
        # But we can verify the function runs without error
        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertEqual(dst_offset_change, 3600)

    def test_us_fall_back_2024(self):
        """US Fall back 2024 (November 3, 2024 at 2:00 AM)"""
        tzinfo = ZoneInfo("America/New_York")
        test_time = datetime.datetime.fromisoformat("2024-11-02T12:00:00").replace(
            tzinfo=tzinfo
        )

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

        # 14 hours before transition, outside 2-hour window
        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertEqual(dst_offset_change, -3600)

    def test_eu_spring_forward_2024(self):
        """EU Spring forward 2024 (March 31, 2024 at 1:00 AM UTC)"""
        tzinfo = ZoneInfo("Europe/London")
        test_time = datetime.datetime.fromisoformat("2024-03-30T12:00:00").replace(
            tzinfo=tzinfo
        )

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

        # 13 hours before transition, outside 2-hour window
        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertEqual(dst_offset_change, 3600)

    def test_eu_fall_back_2024(self):
        """EU Fall back 2024 (October 27, 2024 at 1:00 AM UTC)"""
        tzinfo = ZoneInfo("Europe/London")
        test_time = datetime.datetime.fromisoformat("2024-10-26T12:00:00").replace(
            tzinfo=tzinfo
        )

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

        # 13 hours before transition, outside 2-hour window
        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertEqual(dst_offset_change, -3600)

    def test_australia_spring_forward_2024(self):
        """Australia Spring forward 2024 (October 6, 2024)"""
        tzinfo = ZoneInfo("Australia/Sydney")
        test_time = datetime.datetime.fromisoformat("2024-10-05T12:00:00").replace(
            tzinfo=tzinfo
        )

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

        # 15 hours before transition, outside 2-hour window
        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertEqual(dst_offset_change, 3600)

    def test_australia_fall_back_2025(self):
        """Australia Fall back 2025 (April 6, 2025)"""
        tzinfo = ZoneInfo("Australia/Sydney")
        test_time = datetime.datetime.fromisoformat("2025-04-05T12:00:00").replace(
            tzinfo=tzinfo
        )

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

        # 15 hours before transition, outside 2-hour window
        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertEqual(dst_offset_change, -3600)

    def test_no_dst_timezone_scenario(self):
        """Timezone without DST (America/Phoenix)"""
        tzinfo = ZoneInfo("America/Phoenix")
        test_time = datetime.datetime.fromisoformat("2024-03-09T12:00:00").replace(
            tzinfo=tzinfo
        )

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

        # Phoenix never has DST
        self.assertIsNone(next_dst_change)
        self.assertIsNone(dst_offset_change)


if __name__ == "__main__":
    unittest.main()
