import socket
import os

HOST = '127.0.0.1'
PORT = 5000

username = "alice"
password = "secret123"
filename = "test.txt"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# --- login step ---
login_line = f"{username}|{password}\n"
client_socket.send(login_line.encode())

response = client_socket.recv(1024).decode().strip()
print("Server response:", response)

if response != "OK":
    print("Login failed, aborting.")
    client_socket.close()
    exit()

# --- file transfer step (only runs if login succeeded) ---
filesize = os.path.getsize(filename)
header = f"{filename}|{filesize}\n"
client_socket.send(header.encode())

with open(filename, "rb") as f:
    while True:
        chunk = f.read(4096)
        if not chunk:
            break
        client_socket.send(chunk)

client_socket.close()
print(f"Sent {filename} ({filesize} bytes)")
