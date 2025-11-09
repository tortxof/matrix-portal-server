#!/usr/bin/env python3
"""Test script to verify DST transition detection"""

import datetime
import unittest
from zoneinfo import ZoneInfo

# Import the function from app.py
import sys
sys.path.insert(0, '/home/tortxof/git/matrix-portal-server')
from app import get_next_dst_transition


class TestDSTTransitionDetection(unittest.TestCase):
    """Test DST transition detection for various timezones"""

    def test_america_new_york(self):
        """Test America/New_York timezone (has DST)"""
        tzinfo = ZoneInfo('America/New_York')
        now = datetime.datetime.now(tzinfo)

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, now)

        # Should return valid values or None (depending on time of year)
        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertIsInstance(dst_offset_change, int)
            self.assertIn(dst_offset_change, [3600, -3600])
        else:
            self.assertIsNone(dst_offset_change)

    def test_america_los_angeles(self):
        """Test America/Los_Angeles timezone (has DST)"""
        tzinfo = ZoneInfo('America/Los_Angeles')
        now = datetime.datetime.now(tzinfo)

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, now)

        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertIsInstance(dst_offset_change, int)
            self.assertIn(dst_offset_change, [3600, -3600])
        else:
            self.assertIsNone(dst_offset_change)

    def test_europe_london(self):
        """Test Europe/London timezone (has DST)"""
        tzinfo = ZoneInfo('Europe/London')
        now = datetime.datetime.now(tzinfo)

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, now)

        if next_dst_change is not None:
            self.assertIsInstance(next_dst_change, int)
            self.assertIsInstance(dst_offset_change, int)
            self.assertIn(dst_offset_change, [3600, -3600])
        else:
            self.assertIsNone(dst_offset_change)

    def test_utc(self):
        """Test UTC timezone (no DST)"""
        tzinfo = ZoneInfo('UTC')
        now = datetime.datetime.now(tzinfo)

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, now)

        # UTC never has DST transitions
        self.assertIsNone(next_dst_change)
        self.assertIsNone(dst_offset_change)

    def test_america_phoenix(self):
        """Test America/Phoenix timezone (no DST - Arizona)"""
        tzinfo = ZoneInfo('America/Phoenix')
        now = datetime.datetime.now(tzinfo)

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, now)

        # Arizona doesn't observe DST
        self.assertIsNone(next_dst_change)
        self.assertIsNone(dst_offset_change)

    def test_asia_tokyo(self):
        """Test Asia/Tokyo timezone (no DST)"""
        tzinfo = ZoneInfo('Asia/Tokyo')
        now = datetime.datetime.now(tzinfo)

        next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, now)

        # Japan doesn't observe DST
        self.assertIsNone(next_dst_change)
        self.assertIsNone(dst_offset_change)


if __name__ == '__main__':
    unittest.main()
