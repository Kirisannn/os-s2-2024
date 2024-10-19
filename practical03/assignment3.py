import argparse
import socket
import sys
import threading
import signal
from time import sleep

# Global variables
pattern = ""  # Pattern to search for
global_node_list = []  # List to store all nodes
list_lock = threading.Lock()  # Lock for thread-safe access to global_node_list
books_lock = threading.Lock()  # Lock for thread-safe access to book_map
title_frequencies = {}

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
        self.checked = False  # Flag to check if the node has been checked


class Book:
    def __init__(self, pattern_count=0, last_node=None):
        self.pattern_count = pattern_count
        self.last_node = last_node


class clientHandler(threading.Thread):

    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)  # Initialize new thread
        self.client_socket = client_socket  # The client socket
        self.client_address = client_address  # The client address
        self.head = None  # Head of the book
        self.title_set = False  # Flag to check if title is set
        self.thread_id = self.get_unique_thread_id()  # Unique ID for this thread
        self.file_created = False  # Flag to track if the file has been created

    def get_unique_thread_id(self):
        """Generate a unique ID for the thread."""
        global thread_counter
        with thread_counter_lock:
            thread_counter += 1
            return thread_counter

    def addNode(self, title, line):
        """Add new node to list for given book title"""
        global global_node_list
        global title_frequencies
        global pattern

        # Create new node
        new_node = Node(line, self.head)

        with list_lock:
            if self.head is None:
                # First node of list, set as head
                self.head = new_node
                title = self.head.line.lstrip("\ufeff")[7:]  # Extract title from line

                # Create new book object
                new_book = Book(0, new_node)
                title_frequencies[title] = new_book
            else:
                # Link new node for the same book
                current_node = self.head
                while current_node.book_next is not None:
                    current_node = current_node.book_next

                current_node.book_next = (
                    new_node  # Link new node to end of last node in book
                )

            # Add new node to global list
            try:
                global_node_list.append(new_node)
            except Exception as e:
                print(f"Error: Could not add node to global list. Details:\n{e}", file=sys.stderr)
            finally:
                index = len(global_node_list) - 1
                title = self.head.line.lstrip("\ufeff")[7:]  # Extract title from line

                # If new_node.line contains the pattern, increment the frequency in title_frequencies,
                # Then update the address of the last node in the title_frequencies dictionary
                pattern = pattern
                if title_frequencies[title].last_node.checked:
                    line = new_node.line
                    if pattern in line:
                        title_frequencies[title].pattern_count += 1
                        title_frequencies[title].last_node = new_node
                # elif not title_frequencies[title].last_node.checked:
                else:
                    # Check last node
                    line = title_frequencies[title].last_node.line
                    if pattern in line:
                        title_frequencies[title].pattern_count += 1
                        title_frequencies[title].last_node.checked = True
                    line = new_node.line
                    if pattern in line:
                        title_frequencies[title].pattern_count += 1
                        title_frequencies[title].last_node = new_node

                new_node.checked = True

                print(f"Node {index} added for book titled: {title}")

    def writeToFile(self, initial=False):
        """Write the complete received book to a file according to the thread ID."""
        # Use the thread ID to name the book file
        file_name = f"book_{self.thread_id:02}.txt"

        if initial:
            print(f"Creating file for connection (even if empty): {file_name}")
        else:
            print(f"Updating file with received content: {file_name}")

        try:
            with open(file_name, "w", encoding="utf-8") as file:
                if self.head is None and initial:
                    # No data received yet, create an empty file
                    file.write("")  # Create an empty file for the connection
                    print(f"Empty file {file_name} created.")
                elif self.head is not None:
                    # Write the content to the file (if content exists)
                    current_node = self.head
                    while current_node is not None:
                        file.write(current_node.line)
                        current_node = current_node.book_next
            print(f"File written: {file_name}")
        except IOError as e:
            print(f"Error: Could not write to file {file_name}. Details:\n{e}", file=sys.stderr)

    def run(self):
        print(
            f"---------------------------------------------\nConnection from address: {self.client_address}"
        )
        self.client_socket.setblocking(False)  # Set socket to non-blocking mode
        buffer = bytearray()  # Buffer to store received data

        # Immediately create the file upon connection (even if empty)
        self.writeToFile(initial=True)

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
            print(f"Error: Could not receive data from client. Details:\n{e}", file=sys.stderr)
        finally:
            print("Full book received...")
            self.writeToFile()  # Write to File (final write after connection closes)
            print(f"Connection {self.client_address} closed.\n")
            # Respond to client "Received" message
            self.client_socket.sendall(b"Received\n")
            self.client_socket.close()


class AnalysisThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.daemon = True

    def sort_by_frequency(self):
        global title_frequencies
        # Sort the title_frequencies dictionary by frequency
        sorted_titles = sorted(
            title_frequencies.items(), key=lambda x: x[1].pattern_count, reverse=True
        )

        # Create a new container ordered by the sorted results
        sorted_titles = [(book.pattern_count, title.strip()) for title, book in sorted_titles]

        return sorted_titles

    def run(self):
        global title_frequencies
        while not shutdown_event.is_set():
            with books_lock:
                # Sort the title_frequencies dictionary by frequency
                sorted_titles = self.sort_by_frequency()

            # Print the sorted titles in the format
            # "{rank} --> Book: {book_title}, Pattern: "{search_pattern}", Frequency: {frequency_count}"
            if (self.thread_id == 0) and (sorted_titles != []):
                print("-" * 80)
                for rank, (frequency, title) in enumerate(sorted_titles, start=1):
                    print(f"{rank} --> Book: {title}, Pattern: \"{pattern}\", Frequency: {frequency}")
                print("-" * 80)
            sleep(2) # Sleep for 5 seconds


def shutdown_handler(sig, frame):
    try:
        print("\nShutting down server...")

        # Set shutdown event
        shutdown_event.set()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        print("Server shutdown complete.")
        sys.exit(0)

def main():
    global server_socket
    global pattern
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--port", type=int, help="Desired server port")
    parser.add_argument(
        "-p", "--pattern", type=str, help="Desired pattern to search for"
    )
    args = parser.parse_args()

    # Check port number
    valid_port = False
    if args.port is None:
        print("Please provide a port number...", file=sys.stderr)
    elif args.port < 1025 or args.port > 65535:
        print("Port provided is out of range.\nValid ports include 1025 to 65535...", file=sys.stderr)
    else:
        print("Valid port number detected")
        port = args.port
        valid_port = True

    # Check pattern
    valid_pattern = False
    if args.pattern is None:
        print("Please provide a pattern to search...", file=sys.stderr)
    else:
        print(f"Pattern detected. Searching for: {args.pattern}")
        pattern = args.pattern
        valid_pattern = True

    if not valid_port or not valid_pattern:
        sys.exit(1)

    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)

    # Start 4 AnalysisThreads
    for i in range(4):
        analysis_thread = AnalysisThread(thread_id = i)
        analysis_thread.start()

    # Try to create a socket, bind, and listen
    try:
        server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # Create a socket
        server_socket.bind(("localhost", port))  # Bind to localhost on port
        server_socket.listen(15)  # Start listening for 15 connections
        print(f"Server listening on port {port}...")

    except socket.error as e:
        print(f"Error: Could not create or bind the socket on port {port}. Details:\n{e}", file=sys.stderr)
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
