#!/usr/bin/env python3
"""
Manual demonstration of the time-based filtering system.

This script demonstrates how the system filters drivers based on:
1. Area matching
2. Day-of-week matching
3. Time window matching (within 10 minutes)

It uses the actual database and shows which drivers would be notified
for different ride requests.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

from servertest import get_available_drivers, time_to_seconds
import sqlite3
from datetime import datetime

def seconds_to_time(seconds):
    """Convert seconds since midnight to HH:MM format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

def display_database_state():
    """Display current users and schedules in the database"""
    print("\n" + "="*70)
    print("CURRENT DATABASE STATE")
    print("="*70)
    
    conn = sqlite3.connect('THE.db')
    c = conn.cursor()
    
    # Show drivers
    print("\nDRIVERS:")
    c.execute('''
        SELECT username, area, rating, rating_number 
        FROM users 
        WHERE role='driver'
    ''')
    drivers = c.fetchall()
    
    if not drivers:
        print("  No drivers in database")
    else:
        for username, area, rating, rating_num in drivers:
            print(f"  - {username} (Area: {area}, Rating: {rating:.1f} from {rating_num} ratings)")
            
            # Get schedules for this driver
            c.execute('SELECT day, time FROM schedule WHERE username=?', (username,))
            schedules = c.fetchall()
            
            if schedules:
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                for day, sched_time in schedules:
                    day_name = day_names[day] if 0 <= day <= 6 else f"Day {day}"
                    time_str = seconds_to_time(sched_time)
                    print(f"    {day_name}: {time_str}")
    
    # Show passengers
    print("\nPASSENGERS:")
    c.execute('''
        SELECT username, area 
        FROM users 
        WHERE role='passenger'
    ''')
    passengers = c.fetchall()
    
    if not passengers:
        print("  No passengers in database")
    else:
        for username, area in passengers:
            print(f"  - {username} (Area: {area})")
    
    # Show pending rides
    print("\nPENDING RIDES:")
    c.execute('''
        SELECT id, passenger_username, area, time, status
        FROM rides
        WHERE status='pending'
    ''')
    rides = c.fetchall()
    
    if not rides:
        print("  No pending rides")
    else:
        for ride_id, passenger, area, ride_time, status in rides:
            time_str = seconds_to_time(ride_time)
            print(f"  - Ride #{ride_id}: {passenger} in {area} at {time_str}")
    
    conn.close()

def demonstrate_matching(area, ride_time_str):
    """Demonstrate which drivers would be notified for a given ride request"""
    print("\n" + "="*70)
    print(f"RIDE REQUEST DEMONSTRATION")
    print("="*70)
    
    # Convert time to seconds
    try:
        ride_time = time_to_seconds(ride_time_str)
    except Exception as e:
        print(f"✗ ERROR: Invalid time format: {e}")
        return
    
    print(f"\nRide Request Details:")
    print(f"  Area: {area}")
    print(f"  Time: {ride_time_str} ({ride_time} seconds since midnight)")
    print(f"  Day: {datetime.now().strftime('%A')}")
    
    # Calculate time window
    lower_bound = max(0, ride_time - 10 * 60)
    upper_bound = min(24 * 3600 - 1, ride_time + 10 * 60)
    
    print(f"\nMatching Window (±10 minutes):")
    print(f"  From: {seconds_to_time(lower_bound)}")
    print(f"  To: {seconds_to_time(upper_bound)}")
    
    # Get available drivers
    print("\n[Searching for available drivers...]")
    available_drivers = get_available_drivers(area, ride_time)
    
    print(f"\nDrivers that would be notified: {len(available_drivers)}")
    
    if available_drivers:
        # Get details for each driver
        conn = sqlite3.connect('THE.db')
        c = conn.cursor()
        
        today = datetime.now().weekday()
        
        for driver_username in available_drivers:
            c.execute('SELECT area, rating FROM users WHERE username=?', (driver_username,))
            result = c.fetchone()
            
            if result:
                driver_area, rating = result
                
                # Get their schedule for today
                c.execute('SELECT time FROM schedule WHERE username=? AND day=?', 
                         (driver_username, today))
                sched_result = c.fetchone()
                
                if sched_result:
                    sched_time = sched_result[0]
                    time_diff = abs(sched_time - ride_time)
                    time_diff_min = time_diff // 60
                    
                    print(f"  ✓ {driver_username}")
                    print(f"    - Area: {driver_area}")
                    print(f"    - Schedule: {seconds_to_time(sched_time)}")
                    print(f"    - Time difference: {time_diff_min} minutes")
                    print(f"    - Rating: {rating:.1f}")
        
        conn.close()
    else:
        print("  No matching drivers found")
        print("\nPossible reasons:")
        print("  - No drivers in this area")
        print("  - No drivers scheduled for today")
        print("  - No drivers within 10-minute window of requested time")

def show_all_drivers_schedules_for_today():
    """Show all driver schedules for today"""
    print("\n" + "="*70)
    print(f"ALL DRIVER SCHEDULES FOR TODAY")
    print("="*70)
    
    today = datetime.now().weekday()
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    print(f"\nToday is: {day_names[today]}")
    
    conn = sqlite3.connect('THE.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT u.username, u.area, s.time
        FROM users u
        INNER JOIN schedule s ON u.username = s.username
        WHERE u.role='driver' AND s.day=?
        ORDER BY u.area, s.time
    ''', (today,))
    
    schedules = c.fetchall()
    
    if not schedules:
        print("\nNo drivers scheduled for today")
    else:
        current_area = None
        for username, area, sched_time in schedules:
            if area != current_area:
                print(f"\n{area}:")
                current_area = area
            
            time_str = seconds_to_time(sched_time)
            print(f"  {username} - {time_str}")
    
    conn.close()

def interactive_demo():
    """Run an interactive demonstration"""
    print("\n" + "="*70)
    print("TIME-BASED FILTERING DEMONSTRATION")
    print("="*70)
    
    # Show current state
    display_database_state()
    show_all_drivers_schedules_for_today()
    
    # Demo some common scenarios
    print("\n" + "="*70)
    print("SCENARIO DEMONSTRATIONS")
    print("="*70)
    
    scenarios = [
        ("Hamra", "09:00", "Morning commute - exact match"),
        ("Hamra", "09:05", "Morning commute - 5 min offset"),
        ("Hamra", "09:15", "Outside time window"),
        ("Hamra", "22:00", "Late evening - current pending ride"),
        ("Verdun", "09:00", "Different area"),
    ]
    
    for i, (area, time, description) in enumerate(scenarios, 1):
        print(f"\n{'─'*70}")
        print(f"Scenario {i}: {description}")
        print(f"{'─'*70}")
        demonstrate_matching(area, time)
    
    # Summary
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Drivers are notified only if in the same area")
    print("  2. Drivers must be scheduled for the current day of week")
    print("  3. Driver's schedule must be within ±10 minutes of ride time")
    print("  4. Time is stored as seconds since midnight for precise matching")
    print("  5. The system uses the time_to_seconds() function for consistency")

if __name__ == "__main__":
    interactive_demo()
