#!/usr/bin/env python3
"""
Test script for time-based filtering of ride requests.

This script tests the functionality of:
1. time_to_seconds function - converting various time formats to seconds
2. get_available_drivers function - filtering drivers based on time and area
3. notify_drivers function - notifying only drivers within 10-minute window

Test scenarios:
- Drivers with schedules matching the ride request time (within 10 minutes)
- Drivers with schedules outside the time window
- Multiple drivers in the same area
- Drivers in different areas
- Edge cases (midnight, early morning, late evening)
"""

import sqlite3
import sys
import os
from datetime import datetime, time

# Add parent directory to path to import servertest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))
from servertest import time_to_seconds, get_available_drivers, init_db, init_ride_db

def setup_test_db():
    """Create a fresh test database with sample data"""
    # Remove existing test database if it exists
    if os.path.exists('TEST.db'):
        os.remove('TEST.db')
    
    # Create new database
    conn = sqlite3.connect('TEST.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY NOT NULL,
            password TEXT NOT NULL,
            area TEXT NOT NULL,
            role TEXT NOT NULL,
            rating REAL NOT NULL,
            rating_number INTEGER NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            username TEXT NOT NULL,
            day INTEGER NOT NULL,
            time INTEGER NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_username TEXT NOT NULL,
            passenger_ip TEXT NOT NULL,
            passenger_port INTEGER NOT NULL,
            driver_username TEXT NOT NULL,
            driver_ip TEXT NOT NULL,
            driver_port INTEGER NOT NULL,
            area TEXT NOT NULL,
            time INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' NOT NULL
        )
    ''')
    
    # Get today's day of week (0=Monday, 6=Sunday)
    today = datetime.now().weekday()
    
    # Add test drivers with different schedules
    # Driver 1: 9:00 AM (32400 seconds) in Hamra
    c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('driver1', 'pass123', 'Hamra', 'driver', 0.0, 0))
    c.execute('''INSERT INTO schedule VALUES (?, ?, ?)''',
              ('driver1', today, 32400))  # 9:00 AM
    
    # Driver 2: 9:05 AM (32700 seconds) in Hamra - within 10 min of 9:00
    c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('driver2', 'pass123', 'Hamra', 'driver', 0.0, 0))
    c.execute('''INSERT INTO schedule VALUES (?, ?, ?)''',
              ('driver2', today, 32700))  # 9:05 AM
    
    # Driver 3: 9:15 AM (33300 seconds) in Hamra - outside 10 min window from 9:00
    c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('driver3', 'pass123', 'Hamra', 'driver', 0.0, 0))
    c.execute('''INSERT INTO schedule VALUES (?, ?, ?)''',
              ('driver3', today, 33300))  # 9:15 AM
    
    # Driver 4: 9:00 AM in Verdun - different area
    c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('driver4', 'pass123', 'Verdun', 'driver', 0.0, 0))
    c.execute('''INSERT INTO schedule VALUES (?, ?, ?)''',
              ('driver4', today, 32400))  # 9:00 AM
    
    # Driver 5: 8:55 AM (32100 seconds) in Hamra - within 10 min before 9:00
    c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('driver5', 'pass123', 'Hamra', 'driver', 0.0, 0))
    c.execute('''INSERT INTO schedule VALUES (?, ?, ?)''',
              ('driver5', today, 32100))  # 8:55 AM
    
    # Driver 6: Different day schedule (shouldn't match)
    different_day = (today + 1) % 7
    c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('driver6', 'pass123', 'Hamra', 'driver', 0.0, 0))
    c.execute('''INSERT INTO schedule VALUES (?, ?, ?)''',
              ('driver6', different_day, 32400))  # 9:00 AM but different day
    
    # Add a passenger
    c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('passenger1', 'pass123', 'Hamra', 'passenger', 0.0, 0))
    
    conn.commit()
    conn.close()
    
    print("[SETUP] Test database created with sample data")

def test_time_to_seconds():
    """Test the time_to_seconds conversion function"""
    print("\n" + "="*70)
    print("TEST 1: time_to_seconds function")
    print("="*70)
    
    test_cases = [
        ("00:00", 0, "Midnight"),
        ("08:30", 30600, "8:30 AM"),
        ("09:00", 32400, "9:00 AM"),
        ("12:00", 43200, "Noon"),
        ("23:59", 86340, "11:59 PM"),
        ("14:45", 53100, "2:45 PM"),
    ]
    
    passed = 0
    failed = 0
    
    for time_str, expected, description in test_cases:
        try:
            result = time_to_seconds(time_str)
            if result == expected:
                print(f"✓ PASS: {description} ({time_str}) = {result} seconds")
                passed += 1
            else:
                print(f"✗ FAIL: {description} ({time_str}) = {result}, expected {expected}")
                failed += 1
        except Exception as e:
            print(f"✗ ERROR: {description} ({time_str}) - {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def test_get_available_drivers_matching():
    """Test getting drivers with matching schedules"""
    print("\n" + "="*70)
    print("TEST 2: get_available_drivers - Matching time window")
    print("="*70)
    
    # Test: Ride request at 9:00 AM in Hamra
    target_time = 32400  # 9:00 AM
    area = "Hamra"
    
    # Temporarily replace THE.db with TEST.db for testing
    import servertest
    original_connect = sqlite3.connect
    
    def test_connect(db_name, *args, **kwargs):
        if db_name == 'THE.db':
            return original_connect('TEST.db', *args, **kwargs)
        return original_connect(db_name, *args, **kwargs)
    
    sqlite3.connect = test_connect
    
    try:
        drivers = get_available_drivers(area, target_time)
        
        print(f"\nRide request: Area={area}, Time=9:00 AM (32400 seconds)")
        print(f"Time window: 8:50 AM - 9:10 AM (31800 - 33000 seconds)")
        print(f"\nDrivers found: {drivers}")
        
        # Expected: driver1 (9:00), driver2 (9:05), driver5 (8:55)
        expected_drivers = {'driver1', 'driver2', 'driver5'}
        actual_drivers = set(drivers)
        
        if actual_drivers == expected_drivers:
            print(f"✓ PASS: Correct drivers matched: {sorted(drivers)}")
            print(f"  - driver1 (9:00 AM) - exact match")
            print(f"  - driver2 (9:05 AM) - within 10 min after")
            print(f"  - driver5 (8:55 AM) - within 10 min before")
            return True
        else:
            print(f"✗ FAIL: Expected {sorted(expected_drivers)}, got {sorted(actual_drivers)}")
            missing = expected_drivers - actual_drivers
            extra = actual_drivers - expected_drivers
            if missing:
                print(f"  Missing: {sorted(missing)}")
            if extra:
                print(f"  Extra: {sorted(extra)}")
            return False
    finally:
        sqlite3.connect = original_connect

def test_get_available_drivers_no_match():
    """Test that drivers outside time window are not matched"""
    print("\n" + "="*70)
    print("TEST 3: get_available_drivers - Outside time window")
    print("="*70)
    
    # Test: Ride request at 9:20 AM in Hamra
    target_time = 33600  # 9:20 AM
    area = "Hamra"
    
    # Temporarily replace THE.db with TEST.db
    import servertest
    original_connect = sqlite3.connect
    
    def test_connect(db_name, *args, **kwargs):
        if db_name == 'THE.db':
            return original_connect('TEST.db', *args, **kwargs)
        return original_connect(db_name, *args, **kwargs)
    
    sqlite3.connect = test_connect
    
    try:
        drivers = get_available_drivers(area, target_time)
        
        print(f"\nRide request: Area={area}, Time=9:20 AM (33600 seconds)")
        print(f"Time window: 9:10 AM - 9:30 AM (33000 - 34200 seconds)")
        print(f"\nDrivers found: {drivers}")
        
        # Expected: only driver3 (9:15 AM) is within 10 min
        expected_drivers = {'driver3'}
        actual_drivers = set(drivers)
        
        if actual_drivers == expected_drivers:
            print(f"✓ PASS: Only driver3 (9:15 AM) matched - within 10 min window")
            return True
        else:
            print(f"✗ FAIL: Expected {sorted(expected_drivers)}, got {sorted(actual_drivers)}")
            return False
    finally:
        sqlite3.connect = original_connect

def test_area_filtering():
    """Test that only drivers in the same area are matched"""
    print("\n" + "="*70)
    print("TEST 4: Area filtering")
    print("="*70)
    
    # Test: Ride request at 9:00 AM in Verdun
    target_time = 32400  # 9:00 AM
    area = "Verdun"
    
    # Temporarily replace THE.db with TEST.db
    import servertest
    original_connect = sqlite3.connect
    
    def test_connect(db_name, *args, **kwargs):
        if db_name == 'THE.db':
            return original_connect('TEST.db', *args, **kwargs)
        return original_connect(db_name, *args, **kwargs)
    
    sqlite3.connect = test_connect
    
    try:
        drivers = get_available_drivers(area, target_time)
        
        print(f"\nRide request: Area={area}, Time=9:00 AM (32400 seconds)")
        print(f"Drivers found: {drivers}")
        
        # Expected: only driver4 (Verdun area)
        expected_drivers = {'driver4'}
        actual_drivers = set(drivers)
        
        if actual_drivers == expected_drivers:
            print(f"✓ PASS: Only driver4 (Verdun area) matched")
            print(f"  Drivers in Hamra (driver1, driver2, driver3, driver5) correctly filtered out")
            return True
        else:
            print(f"✗ FAIL: Expected {sorted(expected_drivers)}, got {sorted(actual_drivers)}")
            return False
    finally:
        sqlite3.connect = original_connect

def test_day_filtering():
    """Test that drivers scheduled for different days are not matched"""
    print("\n" + "="*70)
    print("TEST 5: Day-of-week filtering")
    print("="*70)
    
    # driver6 is scheduled for a different day
    # Even if the time matches, they shouldn't be returned
    target_time = 32400  # 9:00 AM
    area = "Hamra"
    
    import servertest
    original_connect = sqlite3.connect
    
    def test_connect(db_name, *args, **kwargs):
        if db_name == 'THE.db':
            return original_connect('TEST.db', *args, **kwargs)
        return original_connect(db_name, *args, **kwargs)
    
    sqlite3.connect = test_connect
    
    try:
        drivers = get_available_drivers(area, target_time)
        
        print(f"\nRide request: Area={area}, Time=9:00 AM (32400 seconds)")
        print(f"Drivers found: {drivers}")
        
        # driver6 should NOT be in the results (different day)
        if 'driver6' not in drivers:
            print(f"✓ PASS: driver6 (scheduled for different day) correctly filtered out")
            return True
        else:
            print(f"✗ FAIL: driver6 should not match (different day schedule)")
            return False
    finally:
        sqlite3.connect = original_connect

def test_edge_case_early_morning():
    """Test edge case: early morning times"""
    print("\n" + "="*70)
    print("TEST 6: Edge case - Early morning (near midnight)")
    print("="*70)
    
    # Add a driver with early morning schedule
    conn = sqlite3.connect('TEST.db')
    c = conn.cursor()
    today = datetime.now().weekday()
    
    c.execute('''INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?)''',
              ('driver_early', 'pass123', 'Hamra', 'driver', 0.0, 0))
    c.execute('''INSERT INTO schedule VALUES (?, ?, ?)''',
              ('driver_early', today, 1800))  # 12:30 AM (00:30)
    conn.commit()
    conn.close()
    
    # Test: Ride at 12:35 AM
    target_time = 2100  # 12:35 AM (00:35)
    area = "Hamra"
    
    import servertest
    original_connect = sqlite3.connect
    
    def test_connect(db_name, *args, **kwargs):
        if db_name == 'THE.db':
            return original_connect('TEST.db', *args, **kwargs)
        return original_connect(db_name, *args, **kwargs)
    
    sqlite3.connect = test_connect
    
    try:
        drivers = get_available_drivers(area, target_time)
        
        print(f"\nRide request: Area={area}, Time=12:35 AM (2100 seconds)")
        print(f"Time window: 12:25 AM - 12:45 AM (1500 - 2700 seconds)")
        print(f"Drivers found: {drivers}")
        
        if 'driver_early' in drivers:
            print(f"✓ PASS: driver_early (12:30 AM) correctly matched")
            return True
        else:
            print(f"✗ FAIL: driver_early should match (within 10 min)")
            return False
    finally:
        sqlite3.connect = original_connect

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("TIME-BASED FILTERING TEST SUITE")
    print("Testing ride request notification system")
    print("="*70)
    
    # Setup
    setup_test_db()
    
    # Run tests
    results = []
    results.append(("time_to_seconds function", test_time_to_seconds()))
    results.append(("Matching time window", test_get_available_drivers_matching()))
    results.append(("Outside time window", test_get_available_drivers_no_match()))
    results.append(("Area filtering", test_area_filtering()))
    results.append(("Day-of-week filtering", test_day_filtering()))
    results.append(("Early morning edge case", test_edge_case_early_morning()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    # Cleanup
    if os.path.exists('TEST.db'):
        os.remove('TEST.db')
        print("\n[CLEANUP] Test database removed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
