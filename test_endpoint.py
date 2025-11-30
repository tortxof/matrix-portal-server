#!/usr/bin/env python3
"""Test the /time endpoint with DST transition fields"""

import datetime
import unittest
from zoneinfo import ZoneInfo

# Import Flask app
import sys
sys.path.insert(0, '/home/tortxof/git/matrix-portal-server')
from app import app


class TestTimeEndpoint(unittest.TestCase):
    """Test the /time endpoint with DST transition fields"""

    def setUp(self):
        """Set up test client"""
        self.client = app.test_client()
        self.location = "40.7128,-74.0060"

    def _test_timezone(self, timezone):
        """Helper method to test a timezone"""
        response = self.client.get(
            '/time',
            headers={
                'X-Timezone': timezone,
                'X-Location': self.location
            }
        )

        self.assertEqual(response.status_code, 200)
        data = response.json

        # Verify response has 4 fields: [timestamp_ms, utc_offset, next_dst_change_ms, new_utc_offset]
        self.assertEqual(len(data), 4, "Response should have 4 fields")

        # Verify timestamp is in milliseconds (should be 13 digits)
        self.assertIsInstance(data[0], int, "Timestamp should be an integer")
        self.assertGreater(data[0], 1000000000000, "Timestamp should be in milliseconds")

        # Verify UTC offset is integer
        self.assertIsInstance(data[1], int, "UTC offset should be an integer")

        # Verify DST fields are either int or None
        self.assertTrue(data[2] is None or isinstance(data[2], int),
                       "next_dst_change should be int or None")
        self.assertTrue(data[3] is None or isinstance(data[3], int),
                       "new_utc_offset should be int or None")

        # If DST transition exists, verify it's in milliseconds and offset change is valid
        if data[2] is not None:
            self.assertGreater(data[2], 1000000000000, "DST change should be in milliseconds")
            self.assertIn(data[3], [3600, -3600],
                         "DST offset change should be ±3600 seconds")

        return data

    def test_america_new_york(self):
        """Test /time endpoint with America/New_York timezone"""
        data = self._test_timezone("America/New_York")
        # Additional assertions can be added here

    def test_america_los_angeles(self):
        """Test /time endpoint with America/Los_Angeles timezone"""
        data = self._test_timezone("America/Los_Angeles")

    def test_europe_london(self):
        """Test /time endpoint with Europe/London timezone"""
        data = self._test_timezone("Europe/London")

    def test_utc(self):
        """Test /time endpoint with UTC timezone (no DST)"""
        data = self._test_timezone("UTC")
        # UTC should never have DST transitions
        self.assertIsNone(data[2], "UTC should have no DST transition")
        self.assertIsNone(data[3], "UTC should have no DST offset change")

    def test_america_phoenix(self):
        """Test /time endpoint with America/Phoenix timezone (no DST)"""
        data = self._test_timezone("America/Phoenix")
        # Phoenix doesn't observe DST
        self.assertIsNone(data[2], "Phoenix should have no DST transition")
        self.assertIsNone(data[3], "Phoenix should have no DST offset change")

    def test_australia_sydney(self):
        """Test /time endpoint with Australia/Sydney timezone"""
        data = self._test_timezone("Australia/Sydney")

    def test_invalid_timezone(self):
        """Test /time endpoint with invalid timezone"""
        response = self.client.get(
            '/time',
            headers={
                'X-Timezone': 'Invalid/Timezone',
                'X-Location': self.location
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_location(self):
        """Test /time endpoint without location header (uses default NYC location)"""
        response = self.client.get(
            '/time',
            headers={
                'X-Timezone': 'America/New_York'
            }
        )
        # Location defaults to NYC (40.7,-74.0), so should return 200
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 4, "Response should have 4 fields")


if __name__ == '__main__':
    unittest.main()
