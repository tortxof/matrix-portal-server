#!/usr/bin/env python3
"""Test script to verify DST transition detection"""

import datetime
from zoneinfo import ZoneInfo

# Import the function from app.py
import sys
sys.path.insert(0, '/home/tortxof/git/matrix-portal-server')
from app import get_next_dst_transition


def test_timezone(tz_name):
    """Test DST transition detection for a given timezone"""
    print(f"\n{'='*60}")
    print(f"Testing timezone: {tz_name}")
    print('='*60)

    tzinfo = ZoneInfo(tz_name)
    now = datetime.datetime.now(tzinfo)

    print(f"Current time: {now}")
    print(f"Current UTC offset: {now.utcoffset()}")
    print(f"Is DST: {now.dst()}")

    next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, now)

    if next_dst_change is None:
        print(f"Result: No DST transition found (both fields are None)")
    else:
        transition_dt = datetime.datetime.fromtimestamp(next_dst_change, tz=tzinfo)
        print(f"Next DST change timestamp: {next_dst_change}")
        print(f"Next DST change datetime: {transition_dt}")
        print(f"DST offset change: {dst_offset_change} seconds ({dst_offset_change/3600:.1f} hours)")

        if dst_offset_change > 0:
            print(f"Direction: Spring forward (gaining daylight)")
        else:
            print(f"Direction: Fall back (losing daylight)")


if __name__ == "__main__":
    # Test various timezones
    test_timezone("America/New_York")  # Has DST
    test_timezone("America/Los_Angeles")  # Has DST
    test_timezone("Europe/London")  # Has DST
    test_timezone("UTC")  # No DST
    test_timezone("America/Phoenix")  # No DST (Arizona)
    test_timezone("Asia/Tokyo")  # No DST
