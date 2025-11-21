# should be a final version istg if this doesnt pay off ill shoot myself
import sqlite3
import json
import socket
import threading
# Keep track of connected drivers: username -> client socket
# Keep track of connected passengers: username -> client socket
connected_drivers = {}
connected_passengers = {}
#template specification
"""
| Column Name          | Type    | Description                                                            
| -------------------- | ------- | ----------------------------------------------------------
|                      |         |                                                           
|                      |         |                                                           
"""
#USER TABLE SPECIFICATION
"""
users TABLE:
| Column Name          | Type    | Description                                                            
| -------------------- | ------- | ------------------------
| username             | TEXT    | unique for each user                                          
| password             | TEXT    | not null        
| area                 | TEXT    | not null 
| role                 | TEXT    | not null
| rating               | REAL    | not null 
| rating_number        | INTEGER | not null          

schedule DB:
| Column Name          | Type    | Description                                                            
| -------------------- | ------- | ------------------------
| username             | TEXT    | n/a
| day                  | INTEGER | (Monday->Sunday) -> (0->6)
| time                 | INTEGER | time of departure to AUB (seconds since mignight)
"""

def init_db():
    conn = sqlite3.connect('THE.db') 
    c = conn.cursor()
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
    conn.commit()  
    conn.close()

# RIDE TABLE SPECIFICATION
"""
| Column Name          | Type    | Description                                                            
| -------------------- | ------- | ----------------------------------------------------------------------|
| `id`                 | INTEGER | Auto-incremented unique ID for each ride request (primary key).       |
| `passenger_username` | TEXT    | The username of the passenger who requested the ride.                 |
| `passenger_ip`       | TEXT    | The passenger's IP address.                                           |
| `passenger_port`     | INTEGER | The passenger's port number.                                          |
| `area`               | TEXT    | The area/zone where the passenger lives.                              |
| `time`               | INTEGER | The requested pickup time as seconds counting from midnight.          |
| `status`             | TEXT    | Current status of the request: "pending", "accepted", or "completed". |
| `driver_username`    | TEXT    | The username of the driver who accepted the ride.                     |
| `driver_ip`          | TEXT    | The driver's IP address.                                              |
| `driver_port`        | INTEGER | The driver's port number.                                             |
"""

def init_ride_db():
    conn = sqlite3.connect('THE.db')
    c = conn.cursor()
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
    conn.commit()
    conn.close()

#convert time string to integer
def time_to_seconds(time_str):
    """
    Converts a time string in "HH:MM" format to seconds since midnight.
    
    Args:
        time_str (str): Time in format "HH:MM" (e.g., "08:30", "14:45", "00:00")
    
    Returns:
        int: Number of seconds since midnight (0-86399)
        
    Raises:
        ValueError: If the time string format is invalid
    
    Examples:
        >>> time_to_seconds("00:00")
        0
        >>> time_to_seconds("08:30")
        30600
        >>> time_to_seconds("23:59")
        86340
    """
    from datetime import datetime
    # Accept several common formats: 24h, with seconds, and 12h with AM/PM
    formats = ['%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M%p']
    last_err = None
    for fmt in formats:
        try:
            t = datetime.strptime(time_str.strip(), fmt).time()
            return t.hour * 3600 + t.minute * 60 + t.second
        except Exception as e:
            last_err = e

    # If we reach here, try a permissive parsing for values like '8:30AM' without space
    try:
        s = time_str.strip()
        if s.lower().endswith(('am', 'pm')) and not s.lower().endswith((' am', ' pm')):
            # insert a space before am/pm
            s = s[:-2] + ' ' + s[-2:]
            t = datetime.strptime(s, '%I:%M %p').time()
            return t.hour * 3600 + t.minute * 60 + t.second
    except Exception:
        pass

    # As a last resort, if input is already numeric seconds, accept it
    try:
        return int(time_str)
    except Exception:
        raise ValueError(f"Unrecognized time format: '{time_str}'")

def convertDayToInt(day):
    if day == "Monday":
        return 0
    elif day == "Tuesday":
        return 1
    elif day == "Wednesday":
        return 2
    elif day == "Thursday":
        return 3
    elif day == "Friday":
        return 4
    elif day == "Saturday":
        return 5
    else:
        return 6
def register_user(data):
    """
    Adds a new user to the database.
    `data` is a dictionary containing: username, password, area, role, rating, rating_number and possibly weekly_schedule 
    Returns a success or error status + success or error message
    """
    try:
        conn = sqlite3.connect('THE.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO users (username, password, area, role, rating, rating_number)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('username'),
            data.get('password'),
            data.get('area'),
            data.get('role'),
            float(data.get('rating', 0.0)),
            int(data.get('rating_number', 0))
        ))

        # If driver provided a weekly schedule, store it in schedules table
        weekly_schedule = data.get('weekly_schedule', None)
        if weekly_schedule and data.get('role') == 'driver':
            if isinstance(weekly_schedule, str):
                schedule_obj = json.loads(weekly_schedule)
            else:
                schedule_obj = weekly_schedule
            for day, timeval in schedule_obj.items():
                # Store time as seconds since midnight for consistency
                day_int = convertDayToInt(day)
                # Convert various time string formats to seconds
                if isinstance(timeval, str):
                    try:
                        seconds = time_to_seconds(timeval)
                    except Exception:
                        # If parsing fails, try trimming seconds portion or raise
                        # attempt to accept 'HH:MM:SS' -> still handled by time_to_seconds
                        seconds = time_to_seconds(timeval)
                else:
                    # If already numeric, store as int
                    seconds = int(timeval)

                c.execute('INSERT INTO schedule (username, day, time) VALUES (?, ?, ?)',
                          (data.get('username'), day_int, int(seconds)))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "User registered successfully"}
    except sqlite3.IntegrityError:
        # Happens if username already exists
        return {"status": "error", "message": "Username already exists"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def login_user(data):
    """
    Authenticates a user using username and password.
    `data` is a dictionary containing: username, password
    Returns success if credentials are correct, else error message
    """
    conn = sqlite3.connect('THE.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM users WHERE username=? AND password=?
    ''', (data['username'], data['password']))
    user = c.fetchone()
    conn.close()
    """
    recall that a row has the following structure:
    user[0->5] : username, password, area, role, weekly_schedule, rating
    """
    if user:
        return {
            "status": "success", 
            "message": "Login successful", 
            "role": user[3], 
            "area": user[2],
            "username": user[0],
        }
    else:
        return {"status": "error", "message": "Invalid username or password"}
    
def create_ride_request(data):
    """
    Adds a new ride request to the rides table.
    `data` is a dictionary containing: passenger_username, passenger_ip, passenger_port, area, time, status
    the driver info is set to null since there is no a
    Returns a success or error message.
    """
    try:
        conn = sqlite3.connect('THE.db')
        c = conn.cursor()
        # Ensure time is stored as seconds since midnight (integer)
        ride_time = data.get('time')
        if isinstance(ride_time, str):
            ride_time = time_to_seconds(ride_time)
        else:
            try:
                ride_time = int(ride_time)
            except Exception:
                ride_time = time_to_seconds(str(ride_time))

        c.execute('''
            INSERT INTO rides (passenger_username, passenger_ip, passenger_port, driver_username, driver_ip, driver_port, area, time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (data['passenger_username'], data['passenger_ip'], data['passenger_port'], '', '', 0, data['area'], int(ride_time), 'pending'))

        # Grab the newly created ride id so we can notify drivers about it
        ride_id = c.lastrowid
        conn.commit()
        conn.close()

        # Build ride info expected by notify_drivers and notify in background
        ride_info = {
            'ride_id': ride_id,
            'passenger_username': data.get('passenger_username'),
            'area': data.get('area'),
            'time': int(ride_time)
        }

        try:
            t = threading.Thread(target=notify_drivers, args=(ride_info,), daemon=True)
            t.start()
        except Exception as e_thread:
            print(f"[WARN] Failed to start notify_drivers thread: {e_thread}")

        return {"status": "success", "message": "Ride request created successfully", "ride_id": ride_id}
    except Exception as e:
        return {"status": "error", "message": f"Failed to create ride request: {e}"}

def notify_drivers(ride_info):
    def get_driver_area(username):
        """
        Returns the area of the driver with the given username.
        Connects to the database, queries the users table for the username, 
        and returns the area if the user exists and is a driver.
        """
        conn = sqlite3.connect('THE.db')
        c = conn.cursor()
        c.execute('''
           SELECT area FROM users
            WHERE username=? AND role='driver'
        ''', (username,))
        result = c.fetchone()  # Fetch the first matching row
        conn.close()
        if result:
            return result[0]  # Return the area
        return "Driver not found!"          # Driver not found
    """
    void function
    Sends a new ride notification to all connected drivers in the given area.
    area: the area of the ride request
    ride_info: dictionary containing ride_id, passenger_username, area, time
    """
    available_drivers = get_available_drivers(ride_info['area'], ride_info['time'])
    # debug print of available drivers (list of usernames)
    print(f"[notify_drivers] matched drivers for area={ride_info['area']} time={ride_info['time']}: {available_drivers}")
    available_usernames = set(available_drivers)

    for username, driver_socket in connected_drivers.items():
        try:
            if username in available_usernames:
                notification = {
                    "action": "new_ride",
                    "passenger_username": ride_info['passenger_username'],
                    "area": ride_info['area'],
                    "time": ride_info['time'],
                    "ride_id": ride_info['ride_id']
                }
                driver_socket.send(json.dumps(notification).encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Could not notify {username}: {e}")

def get_available_drivers(area, time):
    """
    Returns a list of drivers in the specified area who have a schedule
    for today within 10 minutes of the specified time.
    Only returns users with role='driver'.
    
    Args:
        area: The area to search for drivers
        time: The target time to match (datetime.time or string in HH:MM format)
    """
    from datetime import datetime, timedelta

    conn = sqlite3.connect('THE.db')
    c = conn.cursor()

    today = datetime.now().weekday()

    # Normalize target to seconds since midnight
    if isinstance(time, str):
        target_seconds = time_to_seconds(time)
    else:
        try:
            target_seconds = int(time)
        except Exception:
            target_seconds = time_to_seconds(str(time))

    lower = max(0, target_seconds - 10 * 60)
    upper = min(24 * 3600 - 1, target_seconds + 10 * 60)

    # Query all drivers in area for today, then filter by schedule time (robust to stored formats)
    c.execute('''
        SELECT DISTINCT u.username, s.time
        FROM users u
        INNER JOIN schedule s ON u.username = s.username
        WHERE u.role='driver' AND u.area=? AND s.day=?
    ''', (area, today))

    rows = c.fetchall()
    conn.close()

    # Debug info
    print(f"[get_available_drivers] target_seconds={target_seconds}, lower={lower}, upper={upper}")
    print(f"[get_available_drivers] raw rows={rows}")

    matching = []
    for username, s_time in rows:
        try:
            if isinstance(s_time, int):
                sched_seconds = int(s_time)
            else:
                # If stored as 'HH:MM:SS' or 'HH:MM' string, parse
                sched_seconds = time_to_seconds(str(s_time))
        except Exception as e:
            # If parsing fails, skip this schedule entry
            print(f"[get_available_drivers] failed to parse s_time={s_time} for user={username}: {e}")
            continue

        print(f"[get_available_drivers] user={username}, sched_seconds={sched_seconds}")
        if lower <= sched_seconds <= upper:
            matching.append(username)

    return matching


def submit_rating(data):
    """
    data is a dictionary containing (username, rating_value)
    Updates a users rating
    new rating is calculated as (rating * rating_number + rating_value) / rating_number + 1
    """
    try:
        username = data['username']
        rating_value = data['rating_value']
        
        conn = sqlite3.connect('THE.db')
        c = conn.cursor()
        c.execute('''
            SELECT rating, rating_number
            FROM users
            WHERE username=?
        ''', (username,))
        
        result = c.fetchone()
        
        if result is None:
            conn.close()
            return {"success": False, "error": "User not found"}
        current_rating = result[0]
        rating_number = result[1]
        
        # Handle case where rating_number might be None or 0 (new user with no ratings)
        if rating_number is None:
            rating_number = 0
        if current_rating is None:
            current_rating = 0

        new_rating = (current_rating * rating_number + rating_value) / (rating_number + 1)
        new_rating_number = rating_number + 1
        
        # Update the user's rating and rating_number
        c.execute('''
            UPDATE users
            SET rating=?, rating_number=?
            WHERE username=?
        ''', (new_rating, new_rating_number, username))
        conn.commit()
        conn.close()
        return {"success": True, "new_rating": new_rating, "rating_count": new_rating_number}
        
    except Exception as e:
        print(f"[ERROR] Could not submit rating: {e}")
        return {"success": False, "error": str(e)}
def get_average_rating(username):
    """
    returns the rating of a user
    """
    conn = sqlite3.connect('THE.db')
    c = conn.cursor()
    c.execute('''
        SELECT rating FROM users WHERE username = ?
    ''', (username,))
    rating = c.fetchone()
    conn.close()
    if rating is None:
        return None
    return rating[0] # since we get returned a tuple with 1 element


def complete_ride(ride_id, username):
    """
    Marks a ride as completed.
    Only the driver who accepted the ride can complete it.
    """
    try:
        conn = sqlite3.connect('THE.db')
        c = conn.cursor()
        # Only update if the ride is accepted by this driver
        c.execute('''
            UPDATE rides
            SET status='completed'
            WHERE id=? AND driver_username=? AND status='accepted'
        ''', (ride_id, username))
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        if success:
            return {"status": "success", "message": "Ride marked as completed."}
        else:
            return {"status": "error", "message": "Ride cannot be completed (wrong driver or status)."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to complete ride: {e}"}
def accept_ride_request(ride_id, driver_username, driver_ip=None, driver_port=None):
    """
    Updates a ride request as accepted by a driver.
    ride_id: ID of the ride to accept
    driver_username: username of the driver accepting the ride
    Returns True if successful, False if ride was already accepted.
    """
    try:
        conn = sqlite3.connect('THE.db')
        c = conn.cursor()
        
        # Only update if ride is still pending; also store driver's contact info
        if driver_ip is not None and driver_port is not None:
            c.execute('''
                UPDATE rides
                SET status='accepted', driver_username=?, driver_ip=?, driver_port=?
                WHERE id=? AND status='pending'
            ''', (driver_username, driver_ip, driver_port, ride_id))
        else:
            c.execute('''
                UPDATE rides
                SET status='accepted', driver_username=?
                WHERE id=? AND status='pending'
            ''', (driver_username, ride_id))
        
        conn.commit()
        success = c.rowcount > 0  # rowcount > 0 means ride was updated
        conn.close()
        return success
    except Exception as e:
        print(f"[ERROR] Accept ride failed: {e}")
        return False

def handle_client(client_socket, addr):
    """
    Handles a single client connection.
    Receives JSON messages, calls register/login/create_ride, and sends back a response.
    Notifies nearby drivers of new ride requests.
    """
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    while connected:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg:
                break
            data = json.loads(msg)
            action = data.get("action")

            # Call the appropriate function based on action
            if action == "register":
                response = register_user(data)

            elif action == "login":
                response = login_user(data)
                if response["status"] == "success" :
                    if response["role"] == "driver":
                        connected_drivers[data['username']] = client_socket
                        print(f"[INFO] Driver {data['username']} is now connected.")
                    elif response["role"] == "passenger":
                        connected_passengers[data['username']] = client_socket
                        print(f"[INFO] Passenger {data['username']} is now connected.")
 
            elif action == "create_ride":
                # data takes {action; area; time; passenger_username}
                # response contains {status; message}
                response = create_ride_request(data)  # Save ride request in DB
                if response["status"] == "success":
                    ride_info = {
                        'area': data['area'],
                        'time': data['time']
                    }
                    notify_drivers(ride_info)
                    
            elif action == "accept_ride":
                ride_id = data.get("ride_id")
                driver_username = data.get("username") 
                driver_ip = data.get("driver_ip")
                driver_port = data.get("driver_port")

                if accept_ride_request(ride_id, driver_username, driver_ip, driver_port):
                    # Find passenger username and info
                    driver_socket = connected_drivers.get(driver_username)
                    conn_db = sqlite3.connect('THE.db')
                    c_db = conn_db.cursor()
                    c_db.execute('SELECT passenger_username FROM rides WHERE id=?', (ride_id,))
                    result = c_db.fetchone()
                    conn_db.close()

                    if result:
                        passenger_username = result[0]

                        # Get passenger socket if they are online
                        passenger_socket = connected_passengers.get(passenger_username)
                        if passenger_socket:
                            try:
                                # Determine driver contact info: prefer provided values, else derive from socket
                                contact_ip = driver_ip if driver_ip else (driver_socket.getpeername()[0] if driver_socket else None)
                                contact_port = int(driver_port) if driver_port else 6000
                                info = {
                                    "action": "ride_accepted",
                                    "ride_id": ride_id,
                                    "driver_username": driver_username,
                                    "driver_ip": contact_ip,
                                    "driver_port": contact_port
                                }
                                passenger_socket.send(json.dumps(info).encode('utf-8'))
                                print(f"[INFO] Notified passenger {passenger_username} with driver P2P info.")
                            except Exception as e:
                                print(f"[ERROR] Could not notify passenger {passenger_username}: {e}")

                    response = {"status": "success", "message": "Ride accepted successfully."}
                else:
                    response = {"status": "error", "message": "Ride could not be accepted (maybe already taken)."}

            elif action == "get_pending_rides":
                # each element in ride_list is a dictionnary with id, passenger_username, area, time
                area = data.get("area")
                conn = sqlite3.connect('THE.db')
                c = conn.cursor()
                c.execute('''
                    SELECT id, passenger_username, area, time FROM rides
                    WHERE status='pending' AND area=?
                ''', (area,))
                rides = c.fetchall()
                conn.close()

                # Convert each ride tuple to a dictionary for easier handling on client
                ride_list = []
                for ride in rides:
                    ride_list.append({
                        "id": ride[0],
                        "passenger_username": ride[1],
                        "area": ride[2],
                        "time": ride[3]
                    })

                response = {"status": "success", "rides": ride_list}

            elif action == "complete_ride":
                ride_id = data.get("ride_id")
                username = data.get("username")  # should be driver username
                response = complete_ride(ride_id, username)

            elif action == "disconnect":
                connected = False
                response = {"status": "success", "message": "Disconnected"}

                # Remove user from connected lists
                username = data.get("username")
                if username in connected_drivers:
                    del connected_drivers[username]
                if username in connected_passengers:
                    del connected_passengers[username]

            elif action == "submit_rating":
                response = submit_rating(data)

            else:
                response = {"status": "error", "message": "Unknown action"}

            # Send the response back to the client
            client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"[ERROR] {addr} - {e}")
            break

    client_socket.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_server(port):
    """
    Starts the TCP server on the specified port.
    Accepts multiple clients using threads.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
    server.bind(('0.0.0.0', port))  # Bind to all interfaces
    server.listen(5)  # Listen for incoming connections (max 5 in queue)
    print(f"[STARTED] AUBus Server listening on port {port}")

    while True:
        client_socket, addr = server.accept()  # Accept a new connection
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()  # Handle client in a separate thread
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")