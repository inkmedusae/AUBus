import socket

# Connect to driver using IP + port received from server
driver_ip = input("Driver IP: ")
driver_port = int(input("Driver port: "))
ADDR = (driver_ip, driver_port)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print(f"Connected to driver at {ADDR}")

while True:
    msg = input("You: ")
    if msg.lower() == "exit":
        break
    client.send(msg.encode('utf-8'))
    reply = client.recv(1024).decode('utf-8')
    print(f"Driver: {reply}")

client.close()
print("Chat ended.")
