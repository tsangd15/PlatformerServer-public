import socket

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


def send(msg):
    payload = msg.encode(ENCODING)  # encode into byte representation
    payload_size = len(payload)  # get length of payload

    # create header
    header = str(payload_size).encode(ENCODING)
    # pad header so its length is the fixed header size (32)
    header += b" " * (HEADER_SIZE - len(header))

    # send header containing payload size then payload
    client_socket.send(header)
    client_socket.send(payload)
    print(client_socket.recv(2048))


send("123645dcfhdtwetioewh")
