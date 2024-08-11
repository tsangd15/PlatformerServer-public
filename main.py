"""Main Module"""
import socket
import threading
import time
import datetime

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


def log(message):
    print(f"[{datetime.datetime.now()}] >>> {message}")


def handle_client(client_socket, client_addr):
    with client_socket as conn:
        iterations = 0
        while True:
            iterations += 1
            if iterations > 20:
                break
            # receive and decode header (payload size)
            payload_size = conn.recv(HEADER_SIZE).decode(ENCODING)
            # log(f"{client_addr} payload size: '{payload_size}'")
            if payload_size:  # if not empty
                payload_size = int(payload_size)  # convert to int

                # receive payload
                payload = conn.recv(payload_size).decode(ENCODING)
                log(f"payload from {client_addr}: '{payload}'")

                # close both halves of connection
                conn.shutdown(socket.SHUT_RDWR)
                break
            time.sleep(1)

    log(f"CLOSED CONNECTION: {client_addr}")


while True:
    log("Listening...")
    log(f"ACTIVE CONNECTIONS: {threading.active_count()-1}")
    # establish connection with client
    client_socket, client_addr = server_socket.accept()
    log(f"NEW CONNECTION: {client_addr}")

    # create thread for client
    thread = threading.Thread(target=handle_client, args=(client_socket,
                                                          client_addr))

    thread.start()
    # always 1 thread running
    log(f"ACTIVE CONNECTIONS: {threading.active_count()-1}")
