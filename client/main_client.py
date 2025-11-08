# client.py
import socket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (HOST, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print(f"Connected to server at {ADDR}")

while True:
    print("Options: REGISTER, LOGIN, SET_DRIVER, REQUEST_RIDE, EXIT")
    choice = input("Command: ").upper()
    if choice == "EXIT":
        break

    if choice in ["REGISTER", "LOGIN"]:
        username = input("Username: ")
        password = input("Password: ")
        msg = f"{choice}|{username}|{password}"

    elif choice == "SET_DRIVER":
        username = input("Username: ")
        area = input("Area: ")
        schedule = input("Schedule (comma-separated times, e.g. 8:00,17:00): ")
        driver_port = int(input("Driver port to listen for peer chat: "))
        msg = f"{choice}|{username}|{area}|{schedule}|{driver_port}"

    elif choice == "REQUEST_RIDE":
        username = input("Your username: ")
        area = input("Enter your area: ")
        time_req = input("Enter your departure time: ")
        msg = f"{choice}|{username}|{area}|{time_req}"

    else:
        print("Unknown command")
        continue

    client.send(msg.encode('utf-8'))
    reply = client.recv(1024).decode('utf-8')
    print(f"Server: {reply}")

    # Optional: parse driver info for peer-to-peer chat
    parts = reply.split("|")
    if parts[0] == "RIDE_RESPONSE" and parts[1] == "SUCCESS":
        driver_name, driver_ip, driver_port = parts[2], parts[3], int(parts[4])
        print(f"Connect to driver {driver_name} at {driver_ip}:{driver_port} for chat")

client.close()
print("Connection closed.")
