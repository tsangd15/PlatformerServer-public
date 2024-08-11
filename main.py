"""Main Module"""
import socket
import threading
import datetime
import json
from regex import match_addentry, match_get10
from db_handler import add_entry, get_top


def log(message):
    """Print a message to the console with a timestamp."""
    print(f"[{datetime.datetime.now()}] >>> {message}")


def log_connections():
    """Print active connections log message."""
    log(f"ACTIVE CONNECTIONS: {threading.active_count() - initial_threads}")


def send(sock, data):
    """Send data using the given socket.
    A fixed size header containing the size of the data (payload) will be sent
    first so the receiver knows how big the data is.
    The actual data (payload) will be sent afterwards."""
    payload = data.encode(ENCODING)  # encode into byte representation
    payload_size = len(payload)  # get length of payload

    # create header
    header = str(payload_size).encode(ENCODING)
    # pad header so its length is the fixed header size (32)
    header += b" " * (HEADER_SIZE - len(header))

    # send header containing payload size then payload
    sock.send(header)
    sock.send(payload)


def receive(sock):
    """Receive data using the given socket.
    A fixed size header will be received first in order to know the size to
    receive the actual payload (which varies in size).
    The payload is returned."""
    # receive and decode header (containing payload size)
    try:
        header = sock.recv(HEADER_SIZE).decode(ENCODING)
    except ConnectionResetError as e:
        log(f"{e}")
        return None

    if header != "":
        payload_size = int(header)

        # receive and decode payload
        payload = sock.recv(payload_size).decode(ENCODING)
    else:
        log("Receive timed out.")
        payload = None

    return payload


def match(expression):
    if match_addentry(expression):
        # remove command and parentheses from expression
        expression = expression.replace("ADD_ENTRY (", "").replace(")", "")
        tag, score = expression.split(", ")
        score = int(score)

        # carry out add_entry database request
        # returns true if ran, false if input validation error
        return str(add_entry(tag, score))

    elif match_get10(expression):
        # remove command and parentheses from expression
        expression = expression.replace("GET_ENTRIES (", "").replace(")", "")
        quantity = int(expression)

        # carry out get_top database request
        # store results
        results = get_top(quantity)
        # return as json
        return json.dumps(results)

    # no command match
    else:
        return None


def handle_client(client_socket, client_addr):
    """Function for individual thread to run to handle each connection."""
    with client_socket as conn:
        payload = receive(client_socket)
        log(f"payload from {client_addr}: '{payload}'")

        # response == None if invalid command
        response = match(payload)

        # if valid command received, response != None
        if response is not None:
            log(f"responding with: {response}")
            send(conn, response)
        else:
            log("invalid command, closing")

        # close both halves of connection
        conn.shutdown(socket.SHUT_RDWR)

    log(f"CLOSED CONNECTION: {client_addr}")


HEADER_SIZE = 32
IP = "0.0.0.0"  # 0.0.0.0 means listen on every ip assigned to computer
PORT = 63632
SERVER_ADDR = (IP, PORT)
ENCODING = "utf-8"

# create socket object
# socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP protocol
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allow program to take ownership of ip address and port
server_socket.bind(SERVER_ADDR)
# listen on bound port
server_socket.listen(5)  # backlog 5 connections

# connection established
# fixed size prep header contains payload size
# payload (actual data) sent afterwards

# store initial threads (no connection threads)
initial_threads = threading.active_count()

while True:
    log("Listening...")
    log_connections()
    # establish connection with client
    client_socket, client_addr = server_socket.accept()
    log(f"NEW CONNECTION: {client_addr}")

    # create thread for client
    thread = threading.Thread(target=handle_client, args=(client_socket,
                                                          client_addr))

    thread.start()
