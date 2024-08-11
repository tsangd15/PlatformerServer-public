"""Main Module"""
import datetime
import json
import random
import socket
import threading
from queue import Queue
from time import sleep

from db_handler import add_entry, get_top
from regex import match_addentry, match_get10


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
    The actual data (payload) will be sent afterwards.
    The function returns True if it carried out successfully, otherwise False
    is returned."""
    payload = data.encode(ENCODING)  # encode into byte representation
    payload_size = len(payload)  # get length of payload

    # create header
    header = str(payload_size).encode(ENCODING)
    # pad header so its length is the fixed header size (32)
    header += b" " * (HEADER_SIZE - len(header))

    # attempt to send data to recipient
    try:
        # send header containing payload size then payload
        sock.send(header)
        sock.send(payload)
        return True
    # catch connection reset, aborted & refused errors
    except ConnectionError as e:
        log(f"{e}")  # print exception message to console
    return False


def receive(sock):
    """Receive data using the given socket.
    A fixed size header will be received first in order to know the size to
    receive the actual payload (which varies in size).
    The payload is returned."""
    # receive and decode header (containing payload size)
    try:
        header = sock.recv(HEADER_SIZE).decode(ENCODING)
    # catch connection reset, aborted & refused errors
    except ConnectionError as e:
        log(f"{e}")  # print exception message to console
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


def handle_client(client_socket, client_addr, identifier):
    """Function for individual thread to run to handle each connection."""
    with client_socket as conn:
        payload = receive(client_socket)
        log(f"payload from {client_addr}: '{payload}'")

        # enqueue database task
        db_queue.put((identifier, payload))

        # retrieve db task results
        response = get_results(identifier)

        # if valid command received, response != None
        if response is not None:
            log(f"responding with: {response}")
            sent = send(conn, response)
        else:
            log("invalid command, closing")

        # close both halves of connection
        conn.shutdown(socket.SHUT_RDWR)

    log(f"CLOSED CONNECTION: {client_addr}, sent={sent}")


def generate_id():
    """Generate a unique identifier for a thread."""
    while True:
        number = random.randint(1, 50)
        if number not in thread_identifiers:
            thread_identifiers.append(number)
            return number


def get_results(identifier):
    """Return the database task's results.
    The function will try 10 attempts if the task hasn't been completed yet."""
    for _ in range(10):  # counter variable not used so it's named underscore
        if identifier in task_results:
            thread_identifiers.remove(identifier)  # release ID
            return task_results.pop(identifier)
        sleep(2)  # wait 2 seconds before retrying
    return None


def handle_db(queue):
    """Function to handle the tasks in the database task queue.
    This function should run as its own independent thread."""
    while True:
        log(f"db_worker: Queue Size = {queue.qsize()}")
        conn_identifier, conn_payload = queue.get()  # blocking line
        log(f"db_worker: Processing {conn_identifier} // {conn_payload}")
        results = match(conn_payload)
        task_results[conn_identifier] = results


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

# initialise database task firstin-firstout queue
db_queue = Queue(maxsize=15)  # cap queue to 15 tasks

# list of currently unavailable thread ids
thread_identifiers = []

# dictionary of database task results
task_results = {}

# create and start database handling thread which runs the handle_db function
db_thread = threading.Thread(target=handle_db, args=(db_queue,))
db_thread.start()

# store initial threads (no connection threads)
initial_threads = threading.active_count()

while True:
    log_connections()
    # establish connection with client
    client_socket, client_addr = server_socket.accept()
    log(f"NEW CONNECTION: {client_addr}")

    thread_id = generate_id()
    # create thread for client
    thread = threading.Thread(target=handle_client, args=(client_socket,
                                                          client_addr,
                                                          thread_id))

    thread.start()
