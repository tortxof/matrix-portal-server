#!/usr/bin/env python3
"""
Example usage of the /time endpoint with DST transition support
"""

import datetime
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, '/home/tortxof/git/matrix-portal-server')
from app import app


def format_time_response(data, timezone):
    """Format the /time endpoint response in a human-readable way"""
    print(f"\n{'='*70}")
    print(f"Time Information for {timezone}")
    print('='*70)

    # Parse the response
    year, month, day, hour, minute, second = data[0:6]
    weekday, yearday, isdst, microseconds = data[6:10]
    next_dst_change, dst_offset_change = data[10:12]

    # Format current time
    print(f"\nCurrent Time:")
    print(f"  Date: {year}-{month:02d}-{day:02d}")
    print(f"  Time: {hour:02d}:{minute:02d}:{second:02d}.{microseconds:06d}")
    print(f"  Day of week: {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][weekday]}")
    print(f"  Day of year: {yearday}")
    print(f"  Is DST: {'Yes' if isdst else 'No'}")

    # Format DST transition info
    print(f"\nDST Transition Information:")
    if next_dst_change is None:
        print(f"  Status: No DST transitions scheduled")
        print(f"  This timezone does not observe Daylight Saving Time")
    else:
        transition_dt = datetime.datetime.fromtimestamp(
            next_dst_change,
            tz=ZoneInfo(timezone)
        )

        print(f"  Next transition: {transition_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Unix timestamp: {next_dst_change}")
        print(f"  Offset change: {dst_offset_change} seconds")

        if dst_offset_change > 0:
            print(f"  Type: Spring forward (clocks move ahead {dst_offset_change//3600} hour)")
            print(f"  Effect: You 'lose' an hour of sleep")
        else:
            print(f"  Type: Fall back (clocks move back {abs(dst_offset_change)//3600} hour)")
            print(f"  Effect: You 'gain' an hour of sleep")

        # Calculate time until transition
        now = datetime.datetime(year, month, day, hour, minute, second, microseconds)
        now = now.replace(tzinfo=ZoneInfo(timezone))
        time_until = transition_dt - now

        days = time_until.days
        hours = time_until.seconds // 3600
        minutes = (time_until.seconds % 3600) // 60

        print(f"  Time until transition: {days} days, {hours} hours, {minutes} minutes")


def main():
    """Demonstrate the /time endpoint with various timezones"""

    test_cases = [
        ("America/New_York", "40.7128,-74.0060", "New York, USA"),
        ("America/Los_Angeles", "34.0522,-118.2437", "Los Angeles, USA"),
        ("Europe/London", "51.5074,-0.1278", "London, UK"),
        ("Australia/Sydney", "-33.8688,151.2093", "Sydney, Australia"),
        ("America/Phoenix", "33.4484,-112.0740", "Phoenix, USA (No DST)"),
        ("UTC", "0,0", "UTC (No DST)"),
    ]

    with app.test_client() as client:
        for timezone, location, description in test_cases:
            response = client.get(
                '/time',
                headers={
                    'X-Timezone': timezone,
                    'X-Location': location
                }
            )

            if response.status_code == 200:
                print(f"\n\n{'#'*70}")
                print(f"# {description}")
                print(f"{'#'*70}")
                format_time_response(response.json, timezone)
            else:
                print(f"\nError for {timezone}: {response.status_code}")


if __name__ == "__main__":
    main()
