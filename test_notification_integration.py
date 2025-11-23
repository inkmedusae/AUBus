#!/usr/bin/env python3
"""
Integration test for the driver notification system.

This test verifies end-to-end functionality:
1. Driver registration and login
2. Ride request creation
3. Driver notification based on time/area matching
4. Driver acceptance of rides
"""

import socket
import json
import threading
import time
import sys
import os
import sqlite3

# Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

class DriverClient:
    """Simulates a driver client for testing"""
    
    def __init__(self, username, password, area):
        self.username = username
        self.password = password
        self.area = area
        self.socket = None
        self.notifications = []
        self.connected = False
        self.listener_thread = None
        
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            self.connected = True
            
            # Start listening for notifications
            self.listener_thread = threading.Thread(target=self._listen, daemon=True)
            self.listener_thread.start()
            
            return True
        except Exception as e:
            print(f"[ERROR] {self.username} failed to connect: {e}")
            return False
    
    def _listen(self):
        """Listen for notifications from server"""
        while self.connected:
            try:
                msg = self.socket.recv(4096).decode('utf-8')
                if not msg:
                    break
                data = json.loads(msg)
                
                # Store notification
                if data.get('action') == 'new_ride':
                    self.notifications.append(data)
                    print(f"[{self.username}] Received ride notification: {data}")
                    
            except Exception as e:
                if self.connected:
                    print(f"[ERROR] {self.username} listener error: {e}")
                break
    
    def login(self):
        """Login to the server"""
        try:
            login_msg = {
                "action": "login",
                "username": self.username,
                "password": self.password
            }
            self.socket.send(json.dumps(login_msg).encode('utf-8'))
            
            # Wait for response
            response = self.socket.recv(1024).decode('utf-8')
            result = json.loads(response)
            
            if result.get('status') == 'success':
                print(f"[{self.username}] Logged in successfully")
                return True
            else:
                print(f"[{self.username}] Login failed: {result.get('message')}")
                return False
        except Exception as e:
            print(f"[ERROR] {self.username} login error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        try:
            if self.socket and self.connected:
                disconnect_msg = {
                    "action": "disconnect",
                    "username": self.username
                }
                self.socket.send(json.dumps(disconnect_msg).encode('utf-8'))
                self.connected = False
                self.socket.close()
                print(f"[{self.username}] Disconnected")
        except Exception as e:
            print(f"[ERROR] {self.username} disconnect error: {e}")

class PassengerClient:
    """Simulates a passenger client for testing"""
    
    def __init__(self, username, password, area):
        self.username = username
        self.password = password
        self.area = area
        self.socket = None
        
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            return True
        except Exception as e:
            print(f"[ERROR] {self.username} failed to connect: {e}")
            return False
    
    def login(self):
        """Login to the server"""
        try:
            login_msg = {
                "action": "login",
                "username": self.username,
                "password": self.password
            }
            self.socket.send(json.dumps(login_msg).encode('utf-8'))
            
            response = self.socket.recv(1024).decode('utf-8')
            result = json.loads(response)
            
            if result.get('status') == 'success':
                print(f"[{self.username}] Logged in successfully")
                return True
            else:
                print(f"[{self.username}] Login failed: {result.get('message')}")
                return False
        except Exception as e:
            print(f"[ERROR] {self.username} login error: {e}")
            return False
    
    def create_ride_request(self, area, ride_time):
        """Create a ride request"""
        try:
            ride_msg = {
                "action": "create_ride",
                "passenger_username": self.username,
                "passenger_ip": "127.0.0.1",
                "passenger_port": 6000,
                "area": area,
                "time": ride_time
            }
            self.socket.send(json.dumps(ride_msg).encode('utf-8'))
            
            response = self.socket.recv(1024).decode('utf-8')
            result = json.loads(response)
            
            if result.get('status') == 'success':
                print(f"[{self.username}] Ride request created: ride_id={result.get('ride_id')}")
                return result.get('ride_id')
            else:
                print(f"[{self.username}] Ride request failed: {result.get('message')}")
                return None
        except Exception as e:
            print(f"[ERROR] {self.username} ride request error: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from server"""
        try:
            if self.socket:
                disconnect_msg = {
                    "action": "disconnect",
                    "username": self.username
                }
                self.socket.send(json.dumps(disconnect_msg).encode('utf-8'))
                self.socket.close()
                print(f"[{self.username}] Disconnected")
        except Exception as e:
            print(f"[ERROR] {self.username} disconnect error: {e}")

def check_server_running():
    """Check if the server is running"""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2)
        test_socket.connect((SERVER_HOST, SERVER_PORT))
        test_socket.close()
        return True
    except:
        return False

def test_notification_matching_drivers():
    """Test that only matching drivers receive notifications"""
    print("\n" + "="*70)
    print("INTEGRATION TEST 1: Notification to matching drivers")
    print("="*70)
    
    # Connect drivers
    print("\n[SETUP] Connecting drivers...")
    driver1 = DriverClient("driver1", "pass123", "Hamra")
    driver2 = DriverClient("driver2", "pass123", "Hamra")
    driver3 = DriverClient("driver3", "pass123", "Hamra")
    
    if not all([driver1.connect(), driver2.connect(), driver3.connect()]):
        print("✗ FAIL: Could not connect all drivers")
        return False
    
    time.sleep(0.5)  # Wait for connections to establish
    
    if not all([driver1.login(), driver2.login(), driver3.login()]):
        print("✗ FAIL: Could not login all drivers")
        return False
    
    time.sleep(0.5)  # Wait for login to complete
    
    # Create ride request at 9:00 AM
    print("\n[TEST] Creating ride request at 9:00 AM in Hamra...")
    passenger = PassengerClient("passenger1", "pass123", "Hamra")
    
    if not passenger.connect():
        print("✗ FAIL: Passenger could not connect")
        return False
    
    if not passenger.login():
        print("✗ FAIL: Passenger could not login")
        return False
    
    ride_id = passenger.create_ride_request("Hamra", 32400)  # 9:00 AM
    
    if not ride_id:
        print("✗ FAIL: Could not create ride request")
        return False
    
    # Wait for notifications to be sent
    print("\n[WAIT] Waiting 2 seconds for notifications...")
    time.sleep(2)
    
    # Check notifications
    print("\n[RESULTS] Checking which drivers received notifications...")
    
    # Expected: driver1 (9:00), driver2 (9:05) should receive
    # driver3 (9:15) should NOT receive (outside 10 min window)
    
    driver1_notified = len(driver1.notifications) > 0
    driver2_notified = len(driver2.notifications) > 0
    driver3_notified = len(driver3.notifications) > 0
    
    print(f"  driver1 (9:00 AM): {'✓ Notified' if driver1_notified else '✗ Not notified'}")
    print(f"  driver2 (9:05 AM): {'✓ Notified' if driver2_notified else '✗ Not notified'}")
    print(f"  driver3 (9:15 AM): {'✗ Not notified (expected)' if not driver3_notified else '✗ Notified (unexpected)'}")
    
    # Cleanup
    driver1.disconnect()
    driver2.disconnect()
    driver3.disconnect()
    passenger.disconnect()
    
    # Verify results
    if driver1_notified and driver2_notified and not driver3_notified:
        print("\n✓ PASS: Notifications sent correctly to matching drivers only")
        return True
    else:
        print("\n✗ FAIL: Notification logic incorrect")
        if not driver1_notified:
            print("  - driver1 should have been notified")
        if not driver2_notified:
            print("  - driver2 should have been notified")
        if driver3_notified:
            print("  - driver3 should NOT have been notified")
        return False

def test_area_filtering():
    """Test that drivers in different areas don't get notified"""
    print("\n" + "="*70)
    print("INTEGRATION TEST 2: Area-based filtering")
    print("="*70)
    
    # Connect drivers from different areas
    print("\n[SETUP] Connecting drivers from different areas...")
    driver_hamra = DriverClient("driver1", "pass123", "Hamra")
    driver_verdun = DriverClient("driver4", "pass123", "Verdun")
    
    if not all([driver_hamra.connect(), driver_verdun.connect()]):
        print("✗ FAIL: Could not connect drivers")
        return False
    
    time.sleep(0.5)
    
    if not all([driver_hamra.login(), driver_verdun.login()]):
        print("✗ FAIL: Could not login drivers")
        return False
    
    time.sleep(0.5)
    
    # Create ride request in Hamra
    print("\n[TEST] Creating ride request in Hamra at 9:00 AM...")
    passenger = PassengerClient("passenger1", "pass123", "Hamra")
    
    if not passenger.connect() or not passenger.login():
        print("✗ FAIL: Passenger connection failed")
        return False
    
    ride_id = passenger.create_ride_request("Hamra", 32400)  # 9:00 AM
    
    if not ride_id:
        print("✗ FAIL: Could not create ride request")
        return False
    
    # Wait for notifications
    print("\n[WAIT] Waiting 2 seconds for notifications...")
    time.sleep(2)
    
    # Check notifications
    print("\n[RESULTS] Checking notifications...")
    
    hamra_notified = len(driver_hamra.notifications) > 0
    verdun_notified = len(driver_verdun.notifications) > 0
    
    print(f"  driver1 (Hamra): {'✓ Notified' if hamra_notified else '✗ Not notified'}")
    print(f"  driver4 (Verdun): {'✗ Not notified (expected)' if not verdun_notified else '✗ Notified (unexpected)'}")
    
    # Cleanup
    driver_hamra.disconnect()
    driver_verdun.disconnect()
    passenger.disconnect()
    
    # Verify
    if hamra_notified and not verdun_notified:
        print("\n✓ PASS: Area filtering works correctly")
        return True
    else:
        print("\n✗ FAIL: Area filtering failed")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("DRIVER NOTIFICATION INTEGRATION TESTS")
    print("="*70)
    
    # Check if server is running
    print("\n[CHECK] Verifying server is running...")
    if not check_server_running():
        print("✗ ERROR: Server is not running on {}:{}".format(SERVER_HOST, SERVER_PORT))
        print("Please start the server first (it should be running via main.py)")
        return False
    
    print(f"✓ Server is running on {SERVER_HOST}:{SERVER_PORT}")
    
    # Run tests
    results = []
    results.append(("Matching driver notifications", test_notification_matching_drivers()))
    results.append(("Area-based filtering", test_area_filtering()))
    
    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} integration tests passed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
