#!/usr/bin/env python3
"""Test DST transition accuracy to the second with various second values"""

import datetime
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, '/home/tortxof/git/matrix-portal-server')
from app import get_next_dst_transition


def test_transition_accuracy(tz_name, test_time, expected_transition_time):
    """
    Test that DST transition detection is accurate to the second.

    Args:
        tz_name: Timezone name
        test_time: datetime to test from
        expected_transition_time: Expected transition datetime
    """
    print(f"\n{'='*70}")
    print(f"Testing: {tz_name}")
    print(f"Current time: {test_time}")
    print(f"Expected transition: {expected_transition_time}")
    print('='*70)

    tzinfo = ZoneInfo(tz_name)

    next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

    if next_dst_change is None:
        print(f"❌ FAIL: No transition found")
        return False

    transition_dt = datetime.datetime.fromtimestamp(next_dst_change, tz=tzinfo)
    expected_timestamp = int(expected_transition_time.timestamp())

    print(f"Found transition: {transition_dt}")
    print(f"Found timestamp: {next_dst_change}")
    print(f"Expected timestamp: {expected_timestamp}")
    print(f"Offset change: {dst_offset_change} seconds")

    # Check if accurate to the second
    time_diff = abs(next_dst_change - expected_timestamp)

    if time_diff <= 1:
        print(f"✓ PASS: Accurate within 1 second (diff: {time_diff}s)")
        return True
    else:
        print(f"❌ FAIL: Not accurate (diff: {time_diff}s)")
        return False


def test_no_transition(tz_name, test_time):
    """Test that no transition is found when none exists in the 2-hour window"""
    print(f"\n{'='*70}")
    print(f"Testing (no transition expected): {tz_name}")
    print(f"Current time: {test_time}")
    print('='*70)

    tzinfo = ZoneInfo(tz_name)
    next_dst_change, dst_offset_change = get_next_dst_transition(tzinfo, test_time)

    if next_dst_change is None and dst_offset_change is None:
        print(f"✓ PASS: Correctly returned (None, None)")
        return True
    else:
        print(f"❌ FAIL: Expected (None, None), got ({next_dst_change}, {dst_offset_change})")
        return False


if __name__ == "__main__":
    results = []

    # Test 1: US Spring forward 2024 (March 10, 2024 at 2:00:00 AM EST)
    # Testing from 1:23:45 AM (36 minutes 15 seconds before)
    test_time = datetime.datetime(2024, 3, 10, 1, 23, 45, tzinfo=ZoneInfo('America/New_York'))
    expected = datetime.datetime(2024, 3, 10, 2, 0, 0, tzinfo=ZoneInfo('America/New_York'))
    results.append(test_transition_accuracy('America/New_York', test_time, expected))

    # Test 2: US Spring forward from 1:47:33 AM (12 minutes 27 seconds before)
    test_time = datetime.datetime(2024, 3, 10, 1, 47, 33, tzinfo=ZoneInfo('America/New_York'))
    expected = datetime.datetime(2024, 3, 10, 2, 0, 0, tzinfo=ZoneInfo('America/New_York'))
    results.append(test_transition_accuracy('America/New_York', test_time, expected))

    # Test 3: US Fall back 2024 (November 3, 2024 at 2:00:00 AM EDT -> 1:00:00 AM EST)
    # Testing from 1:15:42 AM EDT (44 minutes 18 seconds before)
    # The transition happens at 06:00 UTC, which is 1:00 AM EST (was 2:00 AM EDT)
    test_time = datetime.datetime(2024, 11, 3, 1, 15, 42, tzinfo=ZoneInfo('America/New_York'))
    expected_utc = datetime.datetime(2024, 11, 3, 6, 0, 0, tzinfo=ZoneInfo('UTC'))
    expected = expected_utc.astimezone(ZoneInfo('America/New_York'))
    results.append(test_transition_accuracy('America/New_York', test_time, expected))

    # Test 4: Europe/London Spring forward 2024 (March 31, 2024 at 1:00:00 AM GMT)
    # Testing from 12:37:29 AM (22 minutes 31 seconds before)
    test_time = datetime.datetime(2024, 3, 31, 0, 37, 29, tzinfo=ZoneInfo('Europe/London'))
    expected = datetime.datetime(2024, 3, 31, 1, 0, 0, tzinfo=ZoneInfo('Europe/London'))
    results.append(test_transition_accuracy('Europe/London', test_time, expected))

    # Test 5: Australia/Sydney Fall back 2025 (April 6, 2025 at 3:00:00 AM AEDT -> 2:00:00 AM AEST)
    # Testing from 2:08:17 AM AEDT (51 minutes 43 seconds before)
    # The transition happens at 16:00 UTC (previous day), which is 2:00 AM AEST (was 3:00 AM AEDT)
    test_time = datetime.datetime(2025, 4, 6, 2, 8, 17, tzinfo=ZoneInfo('Australia/Sydney'))
    expected_utc = datetime.datetime(2025, 4, 5, 16, 0, 0, tzinfo=ZoneInfo('UTC'))
    expected = expected_utc.astimezone(ZoneInfo('Australia/Sydney'))
    results.append(test_transition_accuracy('Australia/Sydney', test_time, expected))

    # Test 6: No transition - current time (November 2025)
    test_time = datetime.datetime(2025, 11, 9, 14, 32, 18, tzinfo=ZoneInfo('America/New_York'))
    results.append(test_no_transition('America/New_York', test_time))

    # Test 7: No transition - timezone without DST
    test_time = datetime.datetime(2024, 3, 10, 1, 45, 30, tzinfo=ZoneInfo('America/Phoenix'))
    results.append(test_no_transition('America/Phoenix', test_time))

    # Test 8: Transition just outside 2-hour window (should return None)
    # 2 hours 5 minutes before transition
    test_time = datetime.datetime(2024, 3, 9, 23, 54, 55, tzinfo=ZoneInfo('America/New_York'))
    results.append(test_no_transition('America/New_York', test_time))

    # Test 9: Transition just inside 2-hour window (should find it)
    # 1 hour 59 minutes before transition
    test_time = datetime.datetime(2024, 3, 10, 0, 0, 37, tzinfo=ZoneInfo('America/New_York'))
    expected = datetime.datetime(2024, 3, 10, 2, 0, 0, tzinfo=ZoneInfo('America/New_York'))
    results.append(test_transition_accuracy('America/New_York', test_time, expected))

    # Summary
    print(f"\n\n{'='*70}")
    print(f"TEST SUMMARY")
    print('='*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"❌ {total - passed} TEST(S) FAILED")

    sys.exit(0 if passed == total else 1)
