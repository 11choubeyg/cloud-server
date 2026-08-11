import socket
import os
import threading
from users import check_login

HOST = '127.0.0.1'
PORT = 5000

def read_line(conn):
    """Read bytes from conn until a newline, return decoded string. Returns None if connection closes early."""
    line = b""
    while not line.endswith(b"\n"):
        chunk = conn.recv(1)
        if not chunk:
            return None
        line += chunk
    return line.decode().strip()

def handle_client(conn, addr):
    print(f"[{addr}] Connected")

    # --- login step ---
    login_line = read_line(conn)
    if login_line is None:
        print(f"[{addr}] Disconnected before sending login info.")
        conn.close()
        return

    try:
        username, password = login_line.split("|")
    except ValueError:
        print(f"[{addr}] Malformed login line: {login_line!r}")
        conn.send(b"FAIL\n")
        conn.close()
        return

    if check_login(username, password):
        print(f"[{addr}] Login OK for '{username}'")
        conn.send(b"OK\n")
    else:
        print(f"[{addr}] Login FAILED for '{username}'")
        conn.send(b"FAIL\n")
        conn.close()
        return

    # --- set up this user's private folder ---
    user_folder = f"user_{username}"
    os.makedirs(user_folder, exist_ok=True)

    # --- file transfer step ---
    header = read_line(conn)
    if header is None:
        print(f"[{addr}] Disconnected before sending file header.")
        conn.close()
        return

    try:
        filename, filesize = header.split("|")
        filesize = int(filesize)
    except ValueError:
        print(f"[{addr}] Malformed file header: {header!r}")
        conn.close()
        return

    print(f"[{addr}] Receiving '{filename}' ({filesize} bytes) for user '{username}'...")
    save_path = os.path.join(user_folder, filename)

    received = 0
    with open(save_path, "wb") as f:
        while received < filesize:
            chunk = conn.recv(min(4096, filesize - received))
            if not chunk:
                print(f"[{addr}] Warning: connection dropped early. Got {received}/{filesize} bytes.")
                break
            f.write(chunk)
            received += len(chunk)

    if received == filesize:
        print(f"[{addr}] Saved {received} bytes to {save_path}")
    else:
        print(f"[{addr}] Incomplete transfer: saved {received}/{filesize} bytes to {save_path}")

    conn.close()

# --- main server loop ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}...")

while True:
    conn, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(conn, addr))
    client_thread.start()
