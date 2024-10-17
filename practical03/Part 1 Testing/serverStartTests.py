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
    if output == expected:
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


def test_valid_args_And_send():
    """Test server with valid arguments."""
    print("TEST START: Starting server with valid arguments...")
    results = start_server(["-l", "12345", "-p", "test", "&"])
    sleep(3)

    # Attempt to send a request to the server
    command = ["nc", socket.gethostname(), "12345"]
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
    pretty_test(test_valid_args_And_send)
