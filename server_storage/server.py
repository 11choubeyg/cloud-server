import socket
import os
from users import check_login

HOST = '127.0.0.1'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server listening on {HOST}:{PORT}...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

def read_line(conn):
    """Read bytes from conn until a newline, return decoded string. Returns None if connection closes early."""
    line = b""
    while not line.endswith(b"\n"):
        chunk = conn.recv(1)
        if not chunk:
            return None  # connection closed unexpectedly
        line += chunk
    return line.decode().strip()

# --- login step ---
login_line = read_line(conn)
if login_line is None:
    print("Client disconnected before sending login info.")
    conn.close()
    server_socket.close()
    exit()

try:
    username, password = login_line.split("|")
except ValueError:
    print(f"Malformed login line received: {login_line!r}")
    conn.send(b"FAIL\n")
    conn.close()
    server_socket.close()
    exit()

if check_login(username, password):
    print(f"Login OK for '{username}'")
    conn.send(b"OK\n")
else:
    print(f"Login FAILED for '{username}'")
    conn.send(b"FAIL\n")
    conn.close()
    server_socket.close()
    exit()

# --- set up this user's private folder ---
user_folder = f"user_{username}"
os.makedirs(user_folder, exist_ok=True)

# --- file transfer step ---
header = read_line(conn)
if header is None:
    print("Client disconnected before sending file header.")
    conn.close()
    server_socket.close()
    exit()

try:
    filename, filesize = header.split("|")
    filesize = int(filesize)
except ValueError:
    print(f"Malformed file header received: {header!r}")
    conn.close()
    server_socket.close()
    exit()

print(f"Receiving '{filename}' ({filesize} bytes) for user '{username}'...")

save_path = os.path.join(user_folder, filename)

received = 0
with open(save_path, "wb") as f:
    while received < filesize:
        chunk = conn.recv(min(4096, filesize - received))
        if not chunk:
            print(f"Warning: connection dropped early. Got {received}/{filesize} bytes.")
            break
        f.write(chunk)
        received += len(chunk)

if received == filesize:
    print(f"Saved {received} bytes to {save_path}")
else:
    print(f"Incomplete transfer: saved {received}/{filesize} bytes to {save_path}")

conn.close()
server_socket.close()
