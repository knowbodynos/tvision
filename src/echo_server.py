import socket
import sys
import os


BUF_SIZE = 16


# Read socket_name from input argument
socket_name = sys.argv[1]

# If socket name already exists, unlink it
try:
    os.unlink(socket_name)
except OSError:
    if os.path.exists(socket_name):
        raise

# Create a Unix domain socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind socket at socket_name
print("Binding socket at {}.".format(socket_name))
sock.bind(socket_name)

# Listen for incoming connections
print("Listening for incoming connections.")
sock.listen(1)

# Loop until interrupted
while True:
    print("Waiting for a connection.")
    # Accept a connection from client_address
    connection, client_address = sock.accept()
    try:
        print("Connection from {}.".format(client_address))
        # Receive data from server in chunks of BUF_SIZE bytes
        while True:
            data = connection.recv(BUF_SIZE)
            print("Received [{!r}].".format(data.decode("utf-8")))
            if data:
                print("Echoing data back to client.")
                # Attempty to echo data back to client
                try:
                    connection.sendall(data)
                except BrokenPipeError:
                    pass
            else:
                print("No more data from {}.\n".format(client_address))
                break

    finally:
        connection.close()