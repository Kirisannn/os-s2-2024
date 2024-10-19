import sys
import os
import subprocess
import threading
import argparse


def get_files(directory):
    """Count the number of files in a directory."""
    try:
        files = os.listdir(directory)
        txt_files = [f for f in files if f.endswith(".txt")]
        return txt_files
    except OSError:
        print(f"Error: {directory} is not a valid directory.", file=sys.stderr)
        sys.exit(1)


def thread_worker(thread_id, host, port, file_name):
    print(f"Thread {thread_id} started: Sending {file_name} to {host}.{port}.")
    command = ["nc", str(host), str(port), "-d", "1"]

    # Open the file and pass its contents to the subprocess
    with open("test_input/" + file_name, "r") as file_input:
        result = subprocess.run(
            command, stdin=file_input, capture_output=True, text=True
        )

    # Print the result
    if result.returncode == 0:
        print(f"\nThread {thread_id} finished: Success")
        print(f"Thread {thread_id} Output: {result.stdout}")
    else:
        print(f"\nThread {thread_id} finished: Error")
        print(f"Thread {thread_id} Error:\n{result.stderr}")


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--port", type=int, default=1, help="Port")

    args = argparser.parse_args()
    file_names = get_files("test_input")
    num_threads = len(file_names)
    host = "localhost"
    port = args.port

    threads = []
    for thread_id in range(num_threads):
        thread = threading.Thread(
            target=thread_worker, args=(thread_id, host, port, file_names[thread_id])
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
