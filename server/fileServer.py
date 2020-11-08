import socket
import selectors
import traceback

import libserver

from serverConfig import HOST, PORT


# Inatializing selector
sel = selectors.DefaultSelector()

# Setting up the listening socket
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
print("listening on", (HOST, PORT))
lsock.setblocking(False)

# Registering the listening socket with the selector
sel.register(lsock, selectors.EVENT_READ, data=None)


# This function accepts new connections and registers them with the selector
def accept_connection(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    print(f'\nconnection accepted from {addr}')

    message = libserver.Message(sel, conn, addr)
    # Only asking to check for read now because server will initally always listen for incomming connections
    sel.register(conn, selectors.EVENT_READ, data=message)


try:
    while True:
        events = sel.select(timeout=None)

        for key, mask in events:
            # New connection
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
