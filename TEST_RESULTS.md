# Time-Based Filtering Test Documentation

## Overview

This document describes the testing performed on the AUBus time-based filtering system for ride requests. The system ensures that ride notifications are sent only to drivers who:
1. Are in the same **area** as the passenger
2. Are scheduled for **today's** day of the week
3. Have a schedule within **±10 minutes** of the requested ride time

## Test Files

### 1. `test_time_filtering.py`
**Purpose**: Unit tests for core time filtering functions

**What it tests**:
- `time_to_seconds()` function - converts various time formats to seconds since midnight
- `get_available_drivers()` function - filters drivers based on area, day, and time
- Edge cases: midnight, early morning, late evening times
- Boundary conditions: exactly 10 minutes before/after

**How to run**:
```bash
python3 test_time_filtering.py
```

**Test Results**: ✅ All 6 tests passed
- ✓ time_to_seconds function (6/6 test cases)
- ✓ Matching time window
- ✓ Outside time window  
- ✓ Area filtering
- ✓ Day-of-week filtering
- ✓ Early morning edge case

### 2. `test_notification_integration.py`
**Purpose**: Integration tests for the complete notification system

**What it tests**:
- End-to-end driver notification flow
- Driver registration and login
- Ride request creation
- Notification delivery to connected drivers
- Filtering in a live server environment

**Prerequisites**:
- Server must be running (starts automatically via `main.py`)
- Test users must exist in database

**How to run**:
```bash
# The server starts automatically when running main.py
# Then in a separate terminal:
python3 test_notification_integration.py
```

**Note**: This test requires a running server instance and simulates real client connections.

### 3. `demo_time_filtering.py`
**Purpose**: Interactive demonstration of the filtering system with actual database

**What it shows**:
- Current database state (drivers, passengers, schedules)
- Multiple scenarios showing which drivers get notified
- Explanations of why matches occur or don't occur

**How to run**:
```bash
python3 demo_time_filtering.py
```

**Sample Output Scenarios**:

| Scenario | Area | Time | Expected Result |
|----------|------|------|----------------|
| Morning commute - exact match | Hamra | 09:00 | ✓ Driver notified (exact time match) |
| Morning commute - 5 min offset | Hamra | 09:05 | ✓ Driver notified (within 10 min) |
| Outside time window | Hamra | 09:15 | ✗ No drivers (>10 min difference) |
| Late evening | Hamra | 22:00 | ✗ No drivers (no schedule at that time) |
| Different area | Verdun | 09:00 | ✗ No drivers (area mismatch) |

## How the Time Filtering Works

### 1. Time Conversion
All times are converted to **seconds since midnight** (0-86399) using the `time_to_seconds()` function:
- Midnight (00:00) = 0 seconds
- 9:00 AM = 32,400 seconds
- 10:00 PM (22:00) = 79,200 seconds

This ensures consistent, precise time comparisons.

### 2. Matching Window
For each ride request, the system creates a 20-minute window (±10 minutes):
```python
lower_bound = ride_time - 600  # 10 minutes in seconds
upper_bound = ride_time + 600  # 10 minutes in seconds
```

### 3. Driver Query
The system queries the database for drivers matching ALL criteria:
```sql
SELECT DISTINCT u.username, s.time
FROM users u
INNER JOIN schedule s ON u.username = s.username
WHERE u.role='driver' 
  AND u.area=?           -- Same area
  AND s.day=?            -- Today's day (0=Mon, 6=Sun)
  AND s.time BETWEEN lower_bound AND upper_bound  -- Time window
```

### 4. Notification
Only drivers from the filtered list receive a notification via their socket connection.

## Test Coverage Summary

✅ **Functional Tests**
- Time format conversion (multiple formats: HH:MM, HH:MM:SS, 12-hour with AM/PM)
- Exact time matching
- Time window matching (within ±10 minutes)
- Time window exclusion (outside ±10 minutes)
- Area-based filtering
- Day-of-week filtering
- Edge cases (midnight, early morning, late evening)

✅ **Integration Tests**
- Server connection and authentication
- Real-time notification delivery
- Multiple simultaneous drivers
- Area-based filtering in live environment

✅ **Demonstration**
- Current database state visualization
- Multiple realistic scenarios
- Clear explanations of matching logic

## Known Behavior

### Current Database State
As of the last test run:
- **Drivers**: 1 driver named "driver" in Hamra, scheduled at 09:00 daily
- **Passengers**: 1 passenger named "hi" in Hamra
- **Pending Rides**: Ride #1 at 22:00 (no matching drivers, hence pending)

### Why Ride #1 is Still Pending
The existing ride request is for 22:00 (10 PM), but the only driver is scheduled at 09:00 (9 AM). The time difference is 13 hours, far exceeding the 10-minute matching window, so no drivers are notified.

### How to Create Matching Rides
To test with successful matches, create rides that match driver schedules:
- Area: "Hamra"
- Time: Between 08:50 and 09:10 (any time within ±10 minutes of 09:00)
- Day: Any day of the week (driver is scheduled for all days)

## Code Changes Verified

The following changes were tested and verified:

1. ✅ **notify_drivers function** (servertest.py, lines 292-333)
   - Correctly filters drivers using `get_available_drivers()`
   - Sends notifications only to matching drivers
   - Handles driver socket connections properly

2. ✅ **time_to_seconds function** (servertest.py, lines 97-144)
   - Converts various time formats to integers
   - Used consistently throughout the codebase
   - Handles edge cases and invalid formats

3. ✅ **get_available_drivers function** (servertest.py, lines 335-396)
   - Filters by area, day, and time window
   - Correctly calculates ±10 minute bounds
   - Handles time values stored as both integers and strings

4. ✅ **create_ride_request function** (servertest.py, lines 244-290)
   - Stores time as integer (seconds since midnight)
   - Triggers driver notification in background thread
   - Returns ride_id for tracking

## Recommendations

1. **Add More Test Drivers**: Create drivers in multiple areas with varied schedules to test more scenarios
2. **Test Midnight Wraparound**: Add tests for rides near midnight (23:55, 00:05) to verify boundary handling
3. **Load Testing**: Test with many simultaneous ride requests to verify notification system scales
4. **Error Handling**: Add tests for malformed time inputs and database connection failures

## Conclusion

The time-based filtering system is working correctly and as designed. All unit tests pass, and the demonstration shows the system correctly filtering drivers based on area, day, and time constraints. The 10-minute matching window ensures drivers receive relevant ride requests while avoiding notification overload.
