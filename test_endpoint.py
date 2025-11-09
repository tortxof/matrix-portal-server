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

        # Verify response has 12 fields
        self.assertEqual(len(data), 12, "Response should have 12 fields")

        # Verify basic time fields are integers
        for i in range(10):
            self.assertIsInstance(data[i], int, f"Field {i} should be an integer")

        # Verify DST fields are either int or None
        self.assertTrue(data[10] is None or isinstance(data[10], int),
                       "next_dst_change should be int or None")
        self.assertTrue(data[11] is None or isinstance(data[11], int),
                       "dst_offset_change should be int or None")

        # If DST transition exists, verify offset change is valid
        if data[10] is not None:
            self.assertIn(data[11], [3600, -3600],
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
        self.assertIsNone(data[10], "UTC should have no DST transition")
        self.assertIsNone(data[11], "UTC should have no DST offset change")

    def test_america_phoenix(self):
        """Test /time endpoint with America/Phoenix timezone (no DST)"""
        data = self._test_timezone("America/Phoenix")
        # Phoenix doesn't observe DST
        self.assertIsNone(data[10], "Phoenix should have no DST transition")
        self.assertIsNone(data[11], "Phoenix should have no DST offset change")

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
        """Test /time endpoint without location header"""
        response = self.client.get(
            '/time',
            headers={
                'X-Timezone': 'America/New_York'
            }
        )
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
