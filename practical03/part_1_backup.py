import argparse
import os
import socket
import sys
import threading
import signal

# Global variables
global_node_list = []  # List to store all nodes
list_lock = threading.Lock()  # Lock for thread-safe access to global_node_list
books_lock = threading.Lock()  # Lock for thread-safe access to book_map

server_socket = None  # Server socket
shutdown_event = threading.Event()  # Event to signal shutdown

thread_counter_lock = threading.Lock()
thread_counter = 0  # Global counter to assign unique IDs to threads


class Node:
    def __init__(self, line, head=None):
        self.line = line  # Store the line of data
        self.next = None  # Link to the next node
        self.book_next = None  # Link to the next item in the same book
        self.head = head  # Store the head of the book


class clientHandler(threading.Thread):

    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)  # Initialize new thread
        self.client_socket = client_socket  # The client socket
        self.client_address = client_address  # The client address
        self.head = None  # Head of the book
        self.title_set = False  # Flag to check if title is set
        self.thread_id = self.get_unique_thread_id()  # Unique ID for this thread
        self.file_created = False  # Flag to check if file is created

    def get_unique_thread_id(self):
        """Generate a unique ID for the thread."""
        global thread_counter
        with thread_counter_lock:
            thread_counter += 1
            return thread_counter

    def addNode(self, title, line):
        """Add new node to list for given book title"""
        global global_node_list

        # Create new node
        new_node = Node(line, self.head)

        with list_lock:
            if self.head is None:
                # First node of list, set as head
                self.head = new_node
            else:
                # Link new node for the same book
                current_node = self.head
                while current_node.book_next is not None:
                    current_node = current_node.book_next
                current_node.book_next = new_node  # Link new node

            # Add new node to global list
            try:
                global_node_list.append(new_node)
            except Exception as e:
                print(f"Error: Could not add node to global list. Details:\n{e}")
            finally:
                index = len(global_node_list) - 1
                title = self.head.line.lstrip("\ufeff")[7:]  # Extract title from line

                print(f"Node {index} added for book titled: {title}")

                # If line starts with "\ufeff", remove it
                if line.startswith("\ufeff"):
                    line = line.lstrip("\ufeff")

                # Check if line is the first line of the book
                if line.startswith("Title:") and not self.title_set:
                    with books_lock:
                        title = line.lstrip("\ufeff")[
                            7:
                        ]  # Extract title from line and remove extra spaces
                        self.title_set = True
                        print(f"Book title set: {title}")  # Debugging output

    def writeToFile(self):
        """Write the complete received book to a file according to the thread ID"""
        # Use the thread ID to name the book file
        file_name = f"book_{self.thread_id:02}.txt"

        print(f"Writing to filename: {file_name}")

        # Write book to file without locks
        try:
            with open(file_name, "w", encoding="utf-8") as file:
                current_node = self.head
                while current_node is not None:
                    file.write(current_node.line)
                    current_node = current_node.book_next
            print(f"Book written to file: {file_name}")
        except IOError as e:
            print(f"Error: Could not write to file {file_name}. Details:\n{e}")

    def run(self):
        print(
            f"---------------------------------------------\nConnection from address: {self.client_address}"
        )
        self.client_socket.setblocking(False)  # Set socket to non-blocking mode
        buffer = bytearray()  # Buffer to store received data

        try:
            while not shutdown_event.is_set():
                try:
                    data = self.client_socket.recv(1024)
                    if not data:  # No data received == EOF, connection closed
                        print("EOF received")
                        break
                    buffer.extend(data)  # Store Data in Buffer

                    # Process Complete Lines
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        decoded_line = line.decode("utf-8")

                        # Add node to list
                        title = decoded_line[7:]  # Extract title from line
                        self.addNode(title, decoded_line)

                except BlockingIOError:
                    continue  # No data to receive so continue

        except Exception as e:
            print(f"Error: Could not receive data from client.")
            print(f"Details: {e}")
        finally:
            print("Full book received...")
            self.writeToFile()  # Write to File
            print(f"Connection {self.client_address} closed.\n")
            # Respond to client "Received" message
            self.client_socket.sendall(b"Received\n")
            self.client_socket.close()


def shutdown_handler(sig, frame):
    try:
        print("\nShutting down server...")

        # Set shutdown event
        shutdown_event.set()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Server shutdown complete.")
        sys.exit(0)


def main():
    global server_socket
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--port", type=int, help="Desired server port")
    parser.add_argument(
        "-p", "--pattern", type=str, help="Desired pattern to search for"
    )
    args = parser.parse_args()

    # Check port number
    if args.port is None:
        print("Please provide a port number")
        sys.exit(1)
    elif args.port < 1025 or args.port > 65535:
        print("Port provided is out of range.\nValid ports include 1025 to 65535")
        sys.exit(1)
    else:
        port = args.port

    if args.pattern:
        print(f"Pattern to search for: {args.pattern}")

    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)

    # Try to create a socket, bind, and listen
    try:
        server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # Create a socket
        server_socket.bind((socket.gethostname(), port))  # Bind to localhost on port
        server_socket.listen(15)  # Start listening for 15 connections
        print(f"Server listening on port {port}...")

    except socket.error as e:
        print(f"Error: Could not create or bind the socket on port {port}.")
        print(f"Details: {e}")
        sys.exit(1)

    # Accept incoming connections asynchronously
    while not shutdown_event.is_set():
        try:
            server_socket.settimeout(1.0)
            client_socket, client_address = server_socket.accept()
            handler = clientHandler(client_socket, client_address)
            handler.start()  # Start handler thread
        except socket.timeout:
            continue


if __name__ == "__main__":
    main()
