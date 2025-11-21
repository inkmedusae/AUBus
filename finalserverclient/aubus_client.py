import socket
import json
import threading


"""
example:
response = send_request_to_server('localhost', 5555, {
    "action": "login",
    "username": "ali",
    "password": "pass123"
})
"""
def get_local_ip():
    """Get the local/private IP address of this machine"""
    try:
        # Create a socket connection to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Error getting local IP: {e}"

def send_request_to_server(server_ip, server_port, request_data):
    """
    Connects to the server, sends a JSON request, and receives a JSON response.
    server_ip: IP address of the server
    server_port: Port number of the server
    request_data: Dictionary containing the request (action, username, etc.)
    Returns the server response as a dictionary.
    """
    client = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
        client.settimeout(2)  # Set timeout to 2 seconds
        client.connect((server_ip, server_port))                     # Connect to server
        client.send(json.dumps(request_data).encode('utf-8'))       # Send request as JSON
        response = client.recv(1024).decode('utf-8')               # Receive response
        return json.loads(response)                                 # Convert JSON to dict
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        # Server is not available - return error without printing (caller can handle)
        return {"status": "error", "message": "Connection failed"}
    except Exception as e:
        # Other errors - return error response
        return {"status": "error", "message": f"Error: {str(e)}"}
    finally:
        if client:
            try:
                client.close()  # Always close the socket
            except:
                pass

def listen_for_notifications(client_socket):
    """
    Continuously listens for messages from the server (e.g., new ride notifications).
    Prints the notification to the console when a new ride is available.
    """
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg:
                break
            data = json.loads(msg)
            if data.get("action") == "new_ride":
                print(f"\n[NEW RIDE REQUEST] Passenger: {data['passenger_username']}, "
                       f"Area: {data['area']}, Time: {data['time']}\n> ", end="")
            elif data.get("action") == "ride_accepted":
                driver_ip = data.get("driver_ip")
                driver_port = data.get("driver_port")
                if driver_ip and driver_port:
                    print(f"[INFO] Ride accepted! You can now chat with the driver.")
                    start_chat_with_driver(driver_ip, driver_port)


        except Exception as e:
            print(f"[ERROR] Notification listener: {e}")
            break



SERVER_IP = "127.0.0.1"  # Server IP (localhost for testing)
SERVER_PORT = 5555       # Server port

def client_register(username, password, area, role, rating, rating_number):
    """
    Sends a registration request to the server.
    Returns server response as a dictionary.
    """
    request = {
        "action": "register",
        "username": username,
        "password": password,
        "area": area,
        "role": role,
        "rating": rating,
        "rating_number": rating_number
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)

def client_login(username, password):
    """
    Sends a login request to the server.
    Returns server response as a dictionary.
    """
    request = {
        "action": "login",
        "username": username,
        "password": password
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)

def client_create_ride(passenger_username, area, time):
    """
    Sends a ride request to the server.
    Returns the server response as a dictionary.
    """
    request = {
        "action": "create_ride",
        "passenger_username": passenger_username,
        "passenger_ip": get_local_ip(),
        "passenger_port": 6000,
        "area": area,
        "time": time
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)

def client_get_pending_rides(driver_area):
    """
    Requests the server for all pending rides in the driver's area.
    Returns a list of rides (each ride is a dict with id, passenger_username, area, time)
    """
    request = {
        "action": "get_pending_rides",
        "area": driver_area
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)

def client_accept_ride(ride_id, driver_username):
    """
    Sends a request to the server to accept a ride.
    Returns server response as a dictionary.
    """
    request = {
        "action": "accept_ride",
        "ride_id": ride_id,
        "username": driver_username,
        "driver_ip": get_local_ip(),
        "driver_port": 6000
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)

def connect_to_peer(peer_ip, peer_port):
    """
    Connects to a peer client (driver or passenger) for P2P chat.
    Returns the socket connection object.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer_ip, peer_port))
        print(f"[P2P] Connected to peer at {peer_ip}:{peer_port}")
        return sock
    except Exception as e:
        print(f"[P2P ERROR] Could not connect: {e}")
        return None


def send_p2p_message(peer_socket, message):
    """
    Sends a text message to a peer via P2P connection.
    """
    try:
        peer_socket.send(message.encode('utf-8'))
    except Exception as e:
        print(f"[P2P ERROR] Failed to send message: {e}")

# -----------------------------
# P2P Chat Server (Client Side)
# -----------------------------
def start_p2p_server(username, listen_port=6000):
    """
    Starts a small TCP server to listen for chat messages from a peer.
    - username: your username (for display)
    - listen_port: port to listen on (can be fixed or random)
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', listen_port))
    server.listen(1)
    print(f"[P2P] {username} listening for chat on port {listen_port}...")

    def handle_peer(conn, addr):
        print(f"[P2P] Connected by {addr}")
        while True:
            try:
                msg = conn.recv(1024).decode('utf-8')
                if not msg:
                    break
                print(f"\n[PEER MESSAGE] {msg}\n> ", end="")
            except Exception as e:
                print(f"[P2P ERROR] {e}")
                break
        conn.close()

    def server_loop():
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_peer, args=(conn, addr), daemon=True)
            thread.start()

    threading.Thread(target=server_loop, daemon=True).start()

def start_chat_with_driver(driver_ip, driver_port):
    """
    Connects to a driver for P2P chat and sends messages from console input.
    """
    sock = connect_to_peer(driver_ip, driver_port)
    if not sock:
        print("[ERROR] Could not connect to driver.")
        return

    print("[INFO] Connected! Type messages or 'exit' to leave chat.")
    while True:
        msg = input("> ")
        if msg.lower() == "exit":
            break
        send_p2p_message(sock, msg)
    sock.close()

def client_submit_rating(ride_id, rater_username, ratee_username, score, comment=""):
    request = {
        "action": "submit_rating",
        "ride_id": ride_id,
        "rater_username": rater_username,
        "ratee_username": ratee_username,
        "score": score,
        "comment": comment
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)

def client_get_rating(username):
    request = {
        "action": "get_rating",
        "username": username
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)

def client_complete_ride(ride_id, driver_username):
    request = {
        "action": "complete_ride",
        "ride_id": ride_id,
        "username": driver_username
    }
    return send_request_to_server(SERVER_IP, SERVER_PORT, request)


def main():
    while True:
        print("\n--- AUBus Client ---")
        print("1. Register")
        print("2. Login")
        print("3. Create Ride Request")   # NEW option
        print("4. Exit")
        print("5. View Pending Rides (Driver Only)")
        print("6. Accept a Ride (Driver Only)")
        print("7. Submit Rating")
        print("8. View Average Rating")

        choice = input("Select an option: ")

        if choice == "1":
            name = input("Name: ")
            email = input("Email: ")
            username = input("Username: ")
            password = input("Password: ")
            area = input("Area: ")
            role = input("Role (driver/passenger): ")
            response = client_register(name, email, username, password, area, role)
            print(response)

        elif choice == "2":
            username = input("Username: ")
            password = input("Password: ")

            # Create a persistent socket connection to the server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((SERVER_IP, SERVER_PORT))

                # Send login request
                login_request = {
                    "action": "login",
                    "username": username,
                    "password": password
                }
                client_socket.send(json.dumps(login_request).encode('utf-8'))

                # Receive server response
                response = json.loads(client_socket.recv(1024).decode('utf-8'))
                print(response)

                if response["status"] == "success" :
                    start_p2p_server(username)  
                    # Start notification listener in a separate thread
                    listener_thread = threading.Thread(
                        target=listen_for_notifications,
                        args=(client_socket,),
                        daemon=True
                    )
                    listener_thread.start()
                    print("[INFO] Listening for new ride requests...")

            except Exception as e:
                print(f"[ERROR] Could not connect: {e}")


        elif choice == "3":
            passenger_username = input("Your username: ")
            area = input("Your area: ")
            time = input("Pickup time (e.g., 08:30 AM): ")
            response = client_create_ride(passenger_username, area, time)
            print(response)

        elif choice == "4":
            print("Exiting client.")
            break
        elif choice == "5":  # New option
            driver_area = input("Enter your area: ")
            response = client_get_pending_rides(driver_area)
            if response["status"] == "success":
                rides = response.get("rides", [])
                if not rides:
                    print("No pending rides in your area.")
                else:
                    print("\n--- Pending Rides ---")
                    for ride in rides:
                        print(f"ID: {ride['id']}, Passenger: {ride['passenger_username']}, "
                            f"Area: {ride['area']}, Time: {ride['time']}")
                        
        elif choice == "6":  # Accept a Ride (Driver Only)
            driver_username = input("Enter your username: ")
            ride_id = input("Enter the Ride ID you want to accept: ")

            # Send accept ride request to the server
            response = client_accept_ride(ride_id, driver_username)
            print(response)

            # Check if ride was accepted successfully
            if response.get("status") == "success":
                # If passenger info is returned by server (driver IP/port), start P2P chat
                driver_ip = response.get("driver_ip")      # If server sends back (optional)
                driver_port = response.get("driver_port")  # If server sends back (optional)

                # If you want driver to start chat automatically, you can prompt passenger later
                if driver_ip and driver_port:
                    print(f"[INFO] You can now chat with passenger at {driver_ip}:{driver_port}")
                    start_chat_with_driver(driver_ip, driver_port)

        elif choice == "7":  # Submit Rating
            ride_id = input("Enter Ride ID: ")
            rater = input("Your username: ")
            ratee = input("Ratee username (driver/passenger): ")
            score = int(input("Rating score (1-5): "))
            comment = input("Optional comment: ")
            response = client_submit_rating(ride_id, rater, ratee, score, comment)
            print(response)

        elif choice == "8":  # View Average Rating
            username = input("Enter username to view rating: ")
            response = client_get_rating(username)
            if response["status"] == "success":
                print(f"Average rating for {username}: {response['average_rating']}")
            else:
                print(response["message"])

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
