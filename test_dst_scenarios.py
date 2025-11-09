#!/usr/bin/env python3
"""Test DST transition scenarios with specific dates"""

import datetime
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, '/home/tortxof/git/matrix-portal-server')
from app import get_next_dst_transition


def test_specific_date(tz_name, test_date_str):
    """Test DST transition detection for a specific date"""
    print(f"\n{'='*70}")
    print(f"Testing: {tz_name} on {test_date_str}")
    print('='*70)

    tzinfo = ZoneInfo(tz_name)
    test_time = datetime.datetime.fromisoformat(test_date_str).replace(tzinfo=tzinfo)

    print(f"Test time: {test_time}")
    print(f"UTC offset: {test_time.utcoffset()}")
    print(f"DST offset: {test_time.dst()}")

    next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

    if next_dst_change is None:
        print(f"Result: No DST transition found")
    else:
        transition_dt = datetime.datetime.fromtimestamp(next_dst_change, tz=tzinfo)
        print(f"Next DST change: {transition_dt}")
        print(f"Unix timestamp: {next_dst_change}")
        print(f"Offset change: {dst_offset_change} seconds ({dst_offset_change/3600:.1f} hours)")

        # Calculate time until transition
        time_until = transition_dt - test_time
        print(f"Time until transition: {time_until}")


if __name__ == "__main__":
    # Test scenarios around known DST transitions

    # US Spring forward 2024 (March 10, 2024 at 2:00 AM)
    test_specific_date("America/New_York", "2024-03-09T12:00:00")

    # US Fall back 2024 (November 3, 2024 at 2:00 AM)
    test_specific_date("America/New_York", "2024-11-02T12:00:00")

    # EU Spring forward 2024 (March 31, 2024 at 1:00 AM UTC)
    test_specific_date("Europe/London", "2024-03-30T12:00:00")

    # EU Fall back 2024 (October 27, 2024 at 1:00 AM UTC)
    test_specific_date("Europe/London", "2024-10-26T12:00:00")

    # Australia (Southern Hemisphere - opposite seasons)
    # Spring forward 2024 (October 6, 2024)
    test_specific_date("Australia/Sydney", "2024-10-05T12:00:00")

    # Fall back 2025 (April 6, 2025)
    test_specific_date("Australia/Sydney", "2025-04-05T12:00:00")

    # Timezone without DST
    test_specific_date("America/Phoenix", "2024-03-09T12:00:00")
