#!/usr/bin/env python3
"""Test the /time endpoint with DST transition fields"""

import datetime
from zoneinfo import ZoneInfo

# Import Flask app
import sys
sys.path.insert(0, '/home/tortxof/git/matrix-portal-server')
from app import app


def test_time_endpoint(timezone, location="40.7128,-74.0060"):
    """Test the /time endpoint with a specific timezone"""
    print(f"\n{'='*70}")
    print(f"Testing /time endpoint with timezone: {timezone}")
    print('='*70)

    with app.test_client() as client:
        response = client.get(
            '/time',
            headers={
                'X-Timezone': timezone,
                'X-Location': location
            }
        )

        if response.status_code == 200:
            data = response.json
            print(f"Response: {data}")
            print(f"\nParsed response:")
            print(f"  Year: {data[0]}")
            print(f"  Month: {data[1]}")
            print(f"  Day: {data[2]}")
            print(f"  Hour: {data[3]}")
            print(f"  Minute: {data[4]}")
            print(f"  Second: {data[5]}")
            print(f"  Weekday: {data[6]}")
            print(f"  Year day: {data[7]}")
            print(f"  Is DST: {data[8]}")
            print(f"  Microseconds: {data[9]}")
            print(f"  Next DST change: {data[10]}")
            print(f"  DST offset change: {data[11]}")

            if data[10] is not None:
                transition_dt = datetime.datetime.fromtimestamp(
                    data[10],
                    tz=ZoneInfo(timezone)
                )
                print(f"\n  Next DST transition datetime: {transition_dt}")
                print(f"  Offset change: {data[11]} seconds ({data[11]/3600:.1f} hours)")
                if data[11] > 0:
                    print(f"  Direction: Spring forward")
                else:
                    print(f"  Direction: Fall back")
            else:
                print(f"\n  No DST transition scheduled")
        else:
            print(f"Error: Status code {response.status_code}")
            print(f"Response: {response.data}")


if __name__ == "__main__":
    # Test various timezones
    test_time_endpoint("America/New_York")
    test_time_endpoint("America/Los_Angeles")
    test_time_endpoint("Europe/London")
    test_time_endpoint("UTC")
    test_time_endpoint("America/Phoenix")
    test_time_endpoint("Australia/Sydney")
