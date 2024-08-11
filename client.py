"""Exemplar Client Functions Module"""
import socket
import json


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
    header = sock.recv(HEADER_SIZE).decode(ENCODING)

    if header != "":
        payload_size = int(header)

        # receive and decode payload
        payload = sock.recv(payload_size).decode(ENCODING)
    else:
        payload = None

    return payload


HEADER_SIZE = 32
# specify ip to connect to
IP = "127.0.0.1"
# specify port to bind to
PORT = 63632
SERVER_ADDR = (IP, PORT)
ENCODING = "utf-8"

# create server socket object
# af_inet means ipv4, sock_stream means tcp
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(SERVER_ADDR)

# send(client_socket, "ADD_ENTRY (IJK, 55)")
# print(receive(client_socket))
send(client_socket, "GET_ENTRIES (10)")
print(json.loads(receive(client_socket)))
