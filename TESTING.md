# Testing Guide

This project uses Python's built-in `unittest` framework for testing.

## Running All Tests

To run all tests with verbose output:

```bash
uv run python -m unittest discover -v
```

Or without verbose output:

```bash
uv run python -m unittest discover
```

## Running Specific Test Files

Run a specific test file:

```bash
uv run python -m unittest test_dst_accuracy
uv run python -m unittest test_dst
uv run python -m unittest test_dst_scenarios
uv run python -m unittest test_endpoint
```

## Running Specific Test Classes

Run a specific test class:

```bash
uv run python -m unittest test_dst_accuracy.TestDSTAccuracy
uv run python -m unittest test_endpoint.TestTimeEndpoint
```

## Running Specific Test Methods

Run a specific test method:

```bash
uv run python -m unittest test_dst_accuracy.TestDSTAccuracy.test_us_spring_forward_36min_before
uv run python -m unittest test_endpoint.TestTimeEndpoint.test_america_new_york
```

## Test Files Overview

### `test_dst_accuracy.py` (9 tests)
Tests DST transition detection with second-level accuracy using various non-zero seconds values:
- Spring forward transitions (US, Europe)
- Fall back transitions (US, Australia)
- Edge cases (2-hour boundary)
- No-transition cases

### `test_dst.py` (6 tests)
Tests DST transition detection for various timezones with current time:
- Timezones with DST (America/New_York, America/Los_Angeles, Europe/London)
- Timezones without DST (UTC, America/Phoenix, Asia/Tokyo)

### `test_dst_scenarios.py` (7 tests)
Tests DST transitions around known historical transition dates:
- US transitions (spring/fall 2024)
- EU transitions (spring/fall 2024)
- Australia transitions (spring 2024, fall 2025)
- No-DST timezone scenarios

### `test_endpoint.py` (8 tests)
Tests the `/time` Flask endpoint:
- Various timezones (with and without DST)
- Response format validation
- Error handling (invalid timezone, missing location)

## Test Results

All 30 tests should pass:

```
----------------------------------------------------------------------
Ran 30 tests in 0.009s

OK
```

## Continuous Integration

To integrate with CI/CD, add this to your workflow:

```bash
# Install dependencies
pip install -r requirements.txt  # or use your package manager

# Run tests
python -m unittest discover

# Exit with error code if tests fail
python -m unittest discover || exit 1
```

## Test Coverage

The tests cover:
- ✅ Second-level accuracy for DST transitions
- ✅ Spring forward and fall back transitions
- ✅ Multiple timezones (US, Europe, Australia, Asia)
- ✅ Timezones with and without DST
- ✅ Edge cases (2-hour window boundaries)
- ✅ Flask endpoint functionality
- ✅ Error handling
