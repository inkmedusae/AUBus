import sqlite3

# Keep track of connected drivers: username -> client socket
connected_drivers = {}

# Keep track of connected passengers: username -> client socket
connected_passengers = {}

"""
users TABLE:
┌─────┬─────────────┬──────────────────┬──────────────┬──────────┬──────────┬────────────┐
│ id  │    name     │      email       │  username    │ password │   area   │    role    │
├─────┼─────────────┼──────────────────┼──────────────┼──────────┼──────────┼────────────┤
│  1  │ Ali Hassan  │ ali@aub.edu      │ ali2024      │ pass123  │ Beirut   │ passenger  │
│  2  │ Sara Smith  │ sara@aub.edu     │ sara123      │ pass456  │ Hamra    │ driver     │
│  3  │ John Doe    │ john@aub.edu     │ john_ride    │ pass789  │ Downtown │ passenger  │
└─────┴─────────────┴──────────────────┴──────────────┴──────────┴──────────┴────────────┘
"""


def init_db():
    """
    Creates the SQLite database and a table for users.
    The table stores: id, name, email, username, password, area, role (driver/passenger)
    """
    conn = sqlite3.connect('aubus.db')  # Connects to the database file (creates if not exist)
    c = conn.cursor()                    # Cursor object to execute SQL commands
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            area TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()  # Save changes
    conn.close()   # Close the connection



"""
rides TABLE:
┌─────┬─────────────────────┬──────────┬──────────┬───────────┬─────────────────┐
│ id  │ passenger_username  │  area    │   time   │  status   │ driver_username │
├─────┼─────────────────────┼──────────┼──────────┼───────────┼─────────────────┤
│  1  │ ali2024             │ Beirut   │ 08:30 AM │ pending   │ (empty)         │
│  2  │ sara123             │ Hamra    │ 02:15 PM │ accepted  │ john_driver     │
│  3  │ mike_ride           │ Downtown │ 05:45 PM │ completed │ jane_driver     │
└─────┴─────────────────────┴──────────┴──────────┴───────────┴─────────────────┘



| Column Name          | Type    | Description                                                                                                                  |
| -------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `id`                 | INTEGER | Auto-incremented unique ID for each ride request (primary key).                                                              |
| `passenger_username` | TEXT    | The username of the passenger who requested the ride.                                                                        |
| `area`               | TEXT    | The area/zone where the passenger lives.                                                                                     |
| `time`               | TEXT    | The requested pickup time (stored as a string like `"08:30 AM"`).                                                            |
| `status`             | TEXT    | Current status of the ride request: `"pending"`, `"accepted"`, or `"completed"`. Defaults to `"pending"` when first created. |
| `driver_username`    | TEXT    | The username of the driver who accepted the ride. Empty until a driver accepts.                                              |

"""
def init_ride_db():
    """
    Adds a table for ride requests in the database.
    Stores: id, passenger_username, area, time, status, driver_username
    """
    conn = sqlite3.connect('aubus.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_username TEXT NOT NULL,
            area TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',    -- pending, accepted, completed
            driver_username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_rating_db():
    """
    Creates a ratings table to store ratings between passengers and drivers.
    Columns:
    - id: unique rating ID
    - ride_id: the ride associated with the rating
    - rater_username: the person giving the rating
    - ratee_username: the person receiving the rating
    - score: numeric rating (e.g., 1-5)
    - comment: optional comment
    """
    conn = sqlite3.connect('aubus.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ride_id INTEGER NOT NULL,
            rater_username TEXT NOT NULL,
            ratee_username TEXT NOT NULL,
            score INTEGER NOT NULL,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()



"""
Explanation:
Connects to the database.
Inserts a new user into the users table.
Uses placeholders (?) to safely pass values (prevents SQL injection).
Returns a success message if registration worked.
Returns an error if the username already exists.
"""
def register_user(data):
    """
    Adds a new user to the database.
    `data` is a dictionary containing: name, email, username, password, area, role
    Returns a success or error message
    """
    try:
        conn = sqlite3.connect('aubus.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (name, email, username, password, area, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['username'],
              data['password'], data['area'], data['role']))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "User registered successfully"}
    except sqlite3.IntegrityError:
        # Happens if username already exists
        return {"status": "error", "message": "Username already exists"}




"""
Connects to the database.
Searches for a row where username and password match the input.
Returns success with the user’s role (driver/passenger) and area if found.
Returns error if credentials are incorrect.
"""

def login_user(data):
    """
    Authenticates a user using username and password.
    `data` is a dictionary containing: username, password
    Returns success if credentials are correct, else error
    """
    conn = sqlite3.connect('aubus.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM users WHERE username=? AND password=?
    ''', (data['username'], data['password']))
    user = c.fetchone()  # Fetches the first matching row
    conn.close()

    if user:
        return {"status": "success", "message": "Login successful", "role": user[6], "area": user[5]}
    else:
        return {"status": "error", "message": "Invalid username or password"}



def create_ride_request(data):
    """
    Adds a new ride request to the rides table.
    `data` is a dictionary containing: passenger_username, area, time
    Returns a success or error message.
    """
    try:
        conn = sqlite3.connect('aubus.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO rides (passenger_username, area, time)
            VALUES (?, ?, ?)
        ''', (data['passenger_username'], data['area'], data['time']))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Ride request created successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to create ride request: {e}"}


def get_available_drivers(area):
    """
    Returns a list of drivers in the specified area.
    Only returns users with role='driver'.
    """
    conn = sqlite3.connect('aubus.db')
    c = conn.cursor()
    c.execute('''
        SELECT username, area FROM users
        WHERE role='driver' AND area=?
    ''', (area,))
    drivers = c.fetchall()
    conn.close()
    return drivers  # List of tuples: [(username1, area1), (username2, area2), ...]

def get_driver_area(username):
    """
    Returns the area of the driver with the given username.
    Connects to the database, queries the users table for the username, 
    and returns the area if the user exists and is a driver.
    """
    conn = sqlite3.connect('aubus.db')
    c = conn.cursor()
    c.execute('''
        SELECT area FROM users
        WHERE username=? AND role='driver'
    ''', (username,))
    result = c.fetchone()  # Fetch the first matching row
    conn.close()
    if result:
        return result[0]  # Return the area
    return None          # Driver not found

def notify_drivers(area, ride_info):
    """
    Sends a new ride notification to all connected drivers in the given area.
    area: the area of the ride request
    ride_info: dictionary containing passenger_username, area, time
    """
    for username, driver_socket in connected_drivers.items():
        try:
            # Only notify drivers in the same area
            if get_driver_area(username) == area:
                notification = {
                    "action": "new_ride",
                    "passenger_username": ride_info['passenger_username'],
                    "area": ride_info['area'],
                    "time": ride_info['time']
                }
                driver_socket.send(json.dumps(notification).encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Could not notify {username}: {e}")

def accept_ride_request(ride_id, driver_username):
    """
    Updates a ride request as accepted by a driver.
    ride_id: ID of the ride to accept
    driver_username: username of the driver accepting the ride
    Returns True if successful, False if ride was already accepted.
    """
    try:
        conn = sqlite3.connect('aubus.db')
        c = conn.cursor()
        
        # Only update if ride is still pending
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

def submit_rating(data):
    """
    Adds a rating to the database.
    data: dictionary containing ride_id, rater_username, ratee_username, score, comment
    """
    try:
        conn = sqlite3.connect('aubus.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO ratings (ride_id, rater_username, ratee_username, score, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['ride_id'], data['rater_username'], data['ratee_username'], 
              data['score'], data.get('comment', "")))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Rating submitted successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to submit rating: {e}"}

def get_average_rating(username):
    """
    Returns the average rating of a user.
    """
    conn = sqlite3.connect('aubus.db')
    c = conn.cursor()
    c.execute('''
        SELECT AVG(score) FROM ratings WHERE ratee_username=?
    ''', (username,))
    avg = c.fetchone()[0]
    conn.close()
    if avg:
        return round(avg, 2)
    return None


def complete_ride(ride_id, username):
    """
    Marks a ride as completed.
    Only the driver who accepted the ride can complete it.
    """
    try:
        conn = sqlite3.connect('aubus.db')
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

def get_ride_history(username, role):
    """
    Returns all rides for a user.
    - For passengers: rides they requested
    - For drivers: rides they accepted
    """
    conn = sqlite3.connect('aubus.db')
    c = conn.cursor()
    if role == "passenger":
        c.execute('''
            SELECT id, passenger_username, area, time, status, driver_username
            FROM rides WHERE passenger_username=?
        ''', (username,))
    elif role == "driver":
        c.execute('''
            SELECT id, passenger_username, area, time, status, driver_username
            FROM rides WHERE driver_username=?
        ''', (username,))
    else:
        conn.close()
        return {"status": "error", "message": "Invalid role"}
    
    rides = c.fetchall()
    conn.close()

    ride_list = []
    for ride in rides:
        ride_list.append({
            "id": ride[0],
            "passenger_username": ride[1],
            "area": ride[2],
            "time": ride[3],
            "status": ride[4],
            "driver_username": ride[5]
        })
    
    return {"status": "success", "rides": ride_list}

import socket
import threading
import json
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
                response = create_ride_request(data)  # Save ride request in DB

                if response["status"] == "success":
                    # Find available drivers in the same area
                    drivers = get_available_drivers(data['area'])
                    driver_usernames = [d[0] for d in drivers]
                    print(f"[INFO] Notifying drivers in {data['area']}: {driver_usernames}")
                    
                            # Loop through each driver and send notification if they are connected
                    for driver in drivers:
                        driver_username = driver[0]
                        driver_socket = connected_drivers.get(driver_username)
                        if driver_socket:  # Only notify connected drivers
                            notification = {
                                "action": "new_ride",             # Type of notification
                                "passenger_username": data['passenger_username'],
                                "area": data['area'],
                                "time": data['time']
                            }
                            try:
                                # Send JSON notification to driver
                                driver_socket.send(json.dumps(notification).encode('utf-8'))
                                print(f"[INFO] Notified driver {driver_username} about new ride.")
                            except Exception as e:
                                print(f"[ERROR] Failed to notify {driver_username}: {e}")
            elif action == "accept_ride":
                ride_id = data.get("ride_id")
                driver_username = data.get("username")  # The driver sending the request

                if accept_ride_request(ride_id, driver_username):
                    # Find passenger username and info
                    driver_socket = connected_drivers.get(driver_username) 
                    conn_db = sqlite3.connect('aubus.db')
                    c_db = conn_db.cursor()
                    c_db.execute('SELECT passenger_username FROM rides WHERE id=?', (ride_id,))
                    passenger = c_db.fetchone()
                    conn_db.close()

                    if passenger:
                        passenger_username = passenger[0]

                        # Get passenger socket if they are online
                        passenger_socket = connected_passengers.get(passenger_username)
                        if passenger_socket:
                            try:
                                info = {
                                    "action": "ride_accepted",
                                    "ride_id": ride_id,
                                    "driver_username": driver_username,
                                    "driver_ip": driver_socket.getpeername()[0],  # driver IP
                                    "driver_port": 6000  # fixed P2P port for driver
                                }
                                passenger_socket.send(json.dumps(info).encode('utf-8'))
                                print(f"[INFO] Notified passenger {passenger_username} with driver P2P info.")
                            except Exception as e:
                                print(f"[ERROR] Could not notify passenger {passenger_username}: {e}")


                            passenger_socket = connected_passengers.get(passenger_username)

                            if passenger_socket:
                                try:
                                    passenger_socket.send(json.dumps(info).encode('utf-8'))
                                    print(f"[INFO] Notified passenger {passenger_username} with driver P2P info.")
                                except Exception as e:
                                    print(f"[ERROR] Could not notify passenger {passenger_username}: {e}")

                    response = {"status": "success", "message": "Ride accepted successfully."}
                else:
                    response = {"status": "error", "message": "Ride could not be accepted (maybe already taken)."}

            elif action == "get_pending_rides":
                area = data.get("area")
                conn = sqlite3.connect('aubus.db')
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

            elif action == "get_rating":
                username = data.get("username")
                avg = get_average_rating(username)
                if avg is not None:
                    response = {"status": "success", "average_rating": avg}
                else:
                    response = {"status": "error", "message": "No ratings found"}
            elif action == "get_ride_history":
                username = data.get("username")
                role = data.get("role")  # driver or passenger
                response = get_ride_history(username, role)

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





if __name__ == "__main__":
    init_db()          # Initialize the database and create tables if not exist
    init_ride_db()     # Initialize the rides table for ride requests
    init_rating_db()
    PORT = 5555        # Server port (can also be passed via command line)
    print("[INFO] Starting AUBus server...")
    start_server(PORT) # Start the TCP server

