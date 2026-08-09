import socket

HOST = '127.0.0.1'
PORT = 5000

username = "alice"
password = "secret123"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

login_line = f"{username}|{password}\n"
client_socket.send(login_line.encode())

response = client_socket.recv(1024)
print("Server response:", response.decode().strip())

client_socket.close()
