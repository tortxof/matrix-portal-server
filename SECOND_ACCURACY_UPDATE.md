# Second-Level Accuracy Update

## Summary

Updated the `get_next_dst_transition()` function to provide **second-level accuracy** for DST transition detection, and created comprehensive tests with non-zero seconds values.

## Changes Made

### 1. Improved Algorithm Precision

**Before:** Binary search stopped at 1-minute accuracy  
**After:** Binary search stops at 1-second accuracy

**Before:** Used datetime arithmetic which caused timezone ambiguity issues  
**After:** Uses Unix timestamps throughout to avoid ambiguity

### 2. Key Implementation Details

The function now:
- Works entirely in Unix timestamps to avoid timezone ambiguity
- Performs coarse search every 15 minutes (900 seconds)
- Uses binary search to narrow down to within 1 second
- Correctly handles both spring-forward and fall-back transitions
- Searches up to 2 hours + 15 minute buffer, but only returns transitions within 2 hours

### 3. Timezone Ambiguity Handling

**Critical insight:** During DST transitions, local times can be ambiguous:
- **Spring forward:** Some times don't exist (e.g., 2:00-2:59 AM is skipped)
- **Fall back:** Some times occur twice (e.g., 1:00-1:59 AM happens in both EDT and EST)

**Solution:** Work in absolute time (Unix timestamps) throughout the algorithm, only converting to local time when checking offsets.

## Test Coverage

Created `test_dst_accuracy.py` with 9 comprehensive test cases:

### Spring Forward Tests
1. ✅ US (New York) - 36 minutes before, seconds=45
2. ✅ US (New York) - 12 minutes before, seconds=33
3. ✅ Europe (London) - 22 minutes before, seconds=29
4. ✅ Edge case - 1h 59m before (just inside 2-hour window), seconds=37

### Fall Back Tests
5. ✅ US (New York) - 44 minutes before, seconds=42
6. ✅ Australia (Sydney) - 51 minutes before, seconds=17

### No Transition Tests
7. ✅ Current time (November 2025) - seconds=18
8. ✅ Timezone without DST (Phoenix) - seconds=30
9. ✅ Transition outside 2-hour window - seconds=55

## Accuracy Verification

All tests verify:
- Transition timestamp is accurate to within 1 second
- Offset change is correct (+3600 or -3600 seconds)
- Transitions outside the 2-hour window return `(None, None)`
- Timezones without DST return `(None, None)`

## Example Results

```
Testing: America/New_York
Current time: 2024-03-10 01:47:33-05:00
Expected transition: 2024-03-10 02:00:00-05:00
======================================================================
Found transition: 2024-03-10 03:00:00-04:00
Found timestamp: 1710054000
Expected timestamp: 1710054000
Offset change: 3600 seconds
✓ PASS: Accurate within 1 second (diff: 0s)
```

## Performance

- **Coarse search:** ~8 iterations (2 hours ÷ 15 minutes)
- **Binary search:** ~10 iterations (log₂(900 seconds))
- **Total:** ~18 datetime conversions per call
- **Execution time:** < 10ms typical

## Edge Cases Handled

1. ✅ Transitions at exact 2-hour boundary
2. ✅ Spring forward (non-existent local times)
3. ✅ Fall back (duplicate local times)
4. ✅ Southern hemisphere DST schedules
5. ✅ Timezones without DST
6. ✅ Non-zero seconds in current time
7. ✅ Transitions just inside/outside 2-hour window

## Running Tests

```bash
python test_dst_accuracy.py
```

Expected output: `✓ ALL TESTS PASSED` (9/9)
