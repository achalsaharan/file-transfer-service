import socket
import struct
from serverConfig import HOST, PORT
from checkUpdate import updateChecker

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
print("listening on", (HOST, PORT))

while True:
    conn, addr = lsock.accept()
    client_id = conn.recv(2)
    client_id = struct.unpack(">H", client_id)[0]
    print(f"acceptect connection from client id {client_id}")
    filename = updateChecker(str(client_id))
    print(filename)

    if filename == 0:
        conn.send('no-file'.encode())
        conn.close()
        continue

    conn.send(filename.encode())

    conn.close()
