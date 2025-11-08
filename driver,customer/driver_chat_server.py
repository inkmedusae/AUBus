import socket
import threading

# Driver listens for peer messages (passengers)
HOST = socket.gethostbyname(socket.gethostname())
PORT = int(input("Enter your port to receive passenger messages: "))
ADDR = (HOST, PORT)

driver_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
driver_server.bind(ADDR)
driver_server.listen()
print(f"[DRIVER CHAT SERVER] Listening on {HOST}:{PORT}")

def handle_passenger(conn, addr):
    print(f"[CONNECTED] Passenger {addr} connected.")
    while True:
        msg = conn.recv(1024).decode('utf-8')
        if not msg or msg.lower() == "exit":
            break
        print(f"Passenger: {msg}")
        reply = input("Your reply: ")
        conn.send(reply.encode('utf-8'))
    conn.close()
    print(f"[DISCONNECTED] Passenger {addr}")

while True:
    conn, addr = driver_server.accept()
    threading.Thread(target=handle_passenger, args=(conn, addr)).start()
