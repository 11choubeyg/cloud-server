import socket
from users import check_login

HOST = '127.0.0.1'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server listening on {HOST}:{PORT}...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

# --- login step ---
login_line = b""
while not login_line.endswith(b"\n"):
    login_line += conn.recv(1)
username, password = login_line.decode().strip().split("|")

if check_login(username, password):
    print(f"Login OK for '{username}'")
    conn.send(b"OK\n")
else:
    print(f"Login FAILED for '{username}'")
    conn.send(b"FAIL\n")
    conn.close()
    server_socket.close()
    exit()

# --- file transfer step (only runs if login succeeded) ---
header = b""
while not header.endswith(b"\n"):
    header += conn.recv(1)
filename, filesize = header.decode().strip().split("|")
filesize = int(filesize)
print(f"Receiving '{filename}' ({filesize} bytes)...")

received = 0
with open("received_" + filename, "wb") as f:
    while received < filesize:
        chunk = conn.recv(min(4096, filesize - received))
        if not chunk:
            break
        f.write(chunk)
        received += len(chunk)

print(f"Saved {received} bytes to received_{filename}")
conn.close()
server_socket.close()
