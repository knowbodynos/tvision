import sys
import os

# Include tvision directory in path
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, "..", ".."))

from src.tvision_io import write_to_socket

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Define socket_name and message
    socket_name = dir_path + "/var/run/program.sock"
    message = "Testing socket..."

    # Read timeout from input argument and convert to integer if possible
    timeout = sys.argv[1]
    try:
        timeout = int(timeout)
    except ValueError as ve:
        raise

    # Connect to a Unix domain socket socket_name, write a UTF-8 encoded message message, and receive response from server
    write_to_socket(socket_name, message, timeout=timeout)