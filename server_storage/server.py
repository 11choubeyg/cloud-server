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

# --- read login line ---
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
