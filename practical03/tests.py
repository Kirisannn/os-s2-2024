"""
This script covers testing the following:

1. Starting the server without any arguments
2. Starting the server without a port number
3. Starting the server without a pattern
4. Starting the server with an invalid port number
5. Sending a message to the server (Also checks that server is already running)
"""

import subprocess
from time import sleep
import socket


def start_server(args):
    """Run server with specified arguments."""
    command = ["./assignment3"] + args
    result = subprocess.run(command, capture_output=True, text=True)
    return result


def stop_server():
    """Stop the server."""
    command = ["pkill", "-f", "assignment3"]
    subprocess.run(command)


def pretty_test(test):
    """Runs each test with segregating lines."""
    sleep(1)
    print("=" * 60)
    test()
    print("-" * 60 + "\n")
    stop_server()


def test_no_args():
    """Test server with no arguments."""
    print("TEST START: Starting server without arguments...")
    results = start_server([])
    output = results.stdout
    error = results.stderr
    expected = (
        "Please provide a port number...\nPlease provide a pattern to search...\n"
    )
    print("Error:\n" + error)
    print("Output:\n" + output)
    if not output and error == expected:
        print("TEST RESULT: PASSED")
    elif output:
        print("TEST RESULT: FAILED - Output not empty")
    elif error != expected:
        print("TEST RESULT: FAILED - Error message incorrect")
    else:
        print("TEST RESULT: FAILED")


def test_no_port():
    """Test server with no port number."""
    print("TEST START: Starting server without a port number...")
    results = start_server(["-p", "testNoPort"])
    output = results.stdout
    error = results.stderr
    expected = "Please provide a port number...\n"
    print("Error:\n" + error)
    print("Output:\n" + output)
    if error == expected:
        print("TEST RESULT: PASSED")
    else:
        print("TEST RESULT: FAILED")


def test_no_pattern():
    """Test server with no pattern."""
    print("TEST START: Starting server without a pattern...")
    results = start_server(["-l", "1234"])
    output = results.stdout
    error = results.stderr
    expected = "Please provide a pattern to search...\n"
    print("Error:\n" + error)
    print("Output:\n" + output)
    if error == expected:
        print("TEST RESULT: PASSED")
    else:
        print("TEST RESULT: FAILED")


def test_invalid_port():
    """Test server with an invalid port number."""
    print("TEST START: Starting server with an invalid port number...")
    results = start_server(["-l", "123456", "-p", "testInvalidPort"])
    output = results.stdout
    error = results.stderr
    expected = "Port provided is out of range.\nValid ports include 1025 to 65535...\n"
    print("Error:\n" + error)
    print("Output:\n" + output)
    if error == expected:
        print("TEST RESULT: PASSED")
    else:
        print("TEST RESULT: FAILED")


def test_send():
    """Test receiving a message from the server.
    This test requires the server to be running.
    If successful, the server will print "Received" to the console.

    Starting on 12345

    Would be better to automate this test, but it is difficult to test
    """
    print("Starting server...")
    subprocess.Popen(
        ["./testServer.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    sleep(3)

    print("TEST START: Establishing connection...")

    # Attempt to send a request to the server
    command = ["nc", "localhost", "12345"]
    result = subprocess.run(command, input="test", capture_output=True, text=True)
    output = result.stdout
    error = result.stderr
    expected = "Received\n"
    print("Error:\n" + error)
    print("Output:\n" + output)
    if output == expected:
        print("TEST RESULT: PASSED")
    else:
        print("TEST RESULT: FAILED")


if __name__ == "__main__":
    pretty_test(test_no_args)
    pretty_test(test_no_port)
    pretty_test(test_no_pattern)
    pretty_test(test_invalid_port)
    pretty_test(test_send)
