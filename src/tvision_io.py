import socket
import yaml
from time import time, gmtime, strftime


BUF_SIZE = 16


def print_log(message):
    """Print message with UTC timestamp to STDOUT."""
    timestamp = strftime("[%d %b %Y %H:%M:%S UTC] ", gmtime())
    print(timestamp + message)


def load_config(config_path):
    """Load configuration YAML file to an array of Python dictionaries,
    and sort by time field."""
    try:
        with open(config_path, "r") as config_stream:
            try:
                # Load configuration YAML file
                config = yaml.load(config_stream)
            except Exception as e:
                print_log("{} (Configuration file must be of YAML type.)".format(e))
    except FileNotFoundError as fnf:
        print_log("{} (Configuration file {{{}}} not found.)".format(fnf, config_path))
    # Sort configuration entries on time field
    sorted(config, key=lambda x: x['time'])   
    print_log("Configuration file loaded.")
    return config


def write_to_socket(socket_name, message, timeout=None):
    """Open client connection to a Unix domain socket, write a UTF-8 encoded message,
    and receive response from server."""
    # Get start time
    start_time = time()
    # Create a Unix domain socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Connect to socket as a client
    try:
        sock.connect(socket_name)
    except socket.error as se:
        print_log("{} (Could not connect to socket {{{}}}.)".format(se, socket_name))
    else:
        print_log("Connected to socket {{{}}}.".format(socket_name))
        try:
            # If positive timeout value is specified, set socket timeout
            if not timeout is None:
                if timeout <= 0:
                    ve = "Socket timeout is invalid."
                    print_log("{} (Current socket timeout {{{}}} must be changed to a positive value.)".format(ve, timeout))
                else:
                    sock.settimeout(timeout + start_time - time())
            if (timeout is None) or (timeout > 0):
                # UTF-8 encode message
                message_utf8 = message.encode("utf-8")
                # Send data through socket
                sock.sendall(message_utf8)
                print_log("Sending message {{{}}} to server through socket {{{}}}.".format(message, socket_name))
                amount_received = 0
                amount_expected = len(message_utf8)
                # Receive response from server in chunks of BUF_SIZE bytes
                while (amount_received < amount_expected) and (time() - start_time < timeout):
                    try:
                        # If positive timeout value is specified, set socket timeout
                        if not timeout is None:
                            sock.settimeout(timeout + start_time - time())
                        data = sock.recv(BUF_SIZE)
                    except BlockingIOError as bioe:
                        print_log("{} (Retrying.)".format(bioe))
                    except socket.timeout as st:
                        print_log('{} (Socket {{{}}} timed out after {{{}}} seconds.)'.format(st, socket_name, timeout))
                        break
                    else:
                        amount_received += len(data)
                    print_log('Received message {{{}}} from server.'.format(data.decode("utf-8")))
                if amount_received < amount_expected:
                    raise socket.timeout("timed out")
        except socket.timeout as st:
            print_log('{} (Socket {{{}}} timed out after {{{}}} seconds.)'.format(st, socket_name, timeout))
        print_log("Closing socket {{{}}}.".format(socket_name))
        sock.close()