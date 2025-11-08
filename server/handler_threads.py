# handler_threads.py
users = {}    # Stores username:password
drivers = {}  # Stores driver info: username -> {ip, port, area, schedule}

def handle_client(conn, addr):
    """Handles a single client connection with protocol parsing."""
    print(f"[HANDLER] Handling client {addr}")
    connected = True

    while connected:
        try:
            msg = conn.recv(1024).decode('utf-8')
            if not msg:
                break  # client disconnected

            print(f"[RECEIVED from {addr}] {msg}")
            parts = msg.split("|")
            command = parts[0].upper()

            if command == "REGISTER":
                username, password = parts[1], parts[2]
                if username in users:
                    response = "RESPONSE|FAIL|Username already exists."
                else:
                    users[username] = password
                    response = "RESPONSE|SUCCESS|User registered!"
                conn.send(response.encode('utf-8'))

            elif command == "LOGIN":
                username, password = parts[1], parts[2]
                if username in users and users[username] == password:
                    response = "RESPONSE|SUCCESS|Login successful!"
                else:
                    response = "RESPONSE|FAIL|Invalid username or password."
                conn.send(response.encode('utf-8'))

            elif command == "SET_DRIVER":
                username, area, schedule, driver_port = parts[1], parts[2], parts[3], int(parts[4])
                drivers[username] = {
                    "ip": addr[0],
                    "port": driver_port,
                    "area": area,
                    "schedule": schedule.split(",")
                }
                response = "RESPONSE|SUCCESS|Driver info saved."
                conn.send(response.encode('utf-8'))

            elif command == "REQUEST_RIDE":
                username, area, time_req = parts[1], parts[2], parts[3]
                matched_driver = None
                for driver, info in drivers.items():
                    if info["area"] == area and time_req in info["schedule"]:
                        matched_driver = (driver, info["ip"], info["port"])
                        break

                if matched_driver:
                    driver_name, driver_ip, driver_port = matched_driver
                    response = f"RIDE_RESPONSE|SUCCESS|{driver_name}|{driver_ip}|{driver_port}"
                else:
                    response = "RIDE_RESPONSE|FAIL|No available driver"

                conn.send(response.encode('utf-8'))

            else:
                conn.send("RESPONSE|FAIL|Unknown command.".encode('utf-8'))

        except Exception as e:
            print(f"[ERROR] {addr} -> {e}")
            break

    conn.close()
    print(f"[DISCONNECTED] {addr} connection closed.")
