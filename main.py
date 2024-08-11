"""Main Module"""
import socket
import threading
import datetime


def log(message):
    """Print a message to the console with a timestamp."""
    print(f"[{datetime.datetime.now()}] >>> {message}")


def log_connections():
    """Print active connections log message."""
    log(f"ACTIVE CONNECTIONS: {threading.active_count() - initial_threads}")


def send(sock, msg):
    payload = msg.encode(ENCODING)  # encode into byte representation
    payload_size = len(payload)  # get length of payload

    # create header
    header = str(payload_size).encode(ENCODING)
    # pad header so its length is the fixed header size (32)
    header += b" " * (HEADER_SIZE - len(header))

    # send header containing payload size then payload
    sock.send(header)
    sock.send(payload)


def receive(sock):
    # receive and decode header (containing payload size)
    header = sock.recv(HEADER_SIZE).decode(ENCODING)

    if header != "":
        payload_size = int(header)

        # receive and decode payload
        payload = sock.recv(payload_size).decode(ENCODING)

    return payload


def handle_client(client_socket, client_addr):
    """Function for individual thread to run to handle each connection."""
    with client_socket as conn:
        log(f"payload from {client_addr}: '{receive(client_socket)}'")

        conn.send("affirmative".encode(ENCODING))

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
