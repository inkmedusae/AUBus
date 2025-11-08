# server_main.py
import socket
import threading
from handler_threads import handle_client

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[STARTED] Server running on {HOST}:{PORT}")

def start():
    """Accept new clients and start a thread for each one."""
    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()  
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start()
