# OS - Assignment 03:   Multi-Threaded Network Server for Pattern Analysis


**NOTE:<br>THIS SERVER ASSUMES THAT ALL BOOKS SENT TO IT WILL BE UNIQUE, WITH UNIQUE TITLES & CONTENTS. NO BOOKS SENT TO THE SERVER WILL BE A REPEAT OF A PRE-EXISTING BOOK, OR ONE THAT HAS BEEN SENT BEFORE IN THE CURRENT RUNNING INSTANCE OF THE SERVER.**

**IMPLEMENTATION HAS BEEN DEVELOPED IN A ANACONDA3 ENVIRONMENT WITH PYTHON VER. 3.12.7**

## 1. Running the Server

To run the server, use the following command format in your shell terminal.

```
./assignment03 -l <port> -p <pattern>
```

Example:

```
./assignment03 -l 12345 -p happy
```

In the example above,
- "12345" is the port desired. Valid ports range between 1025 - 65535, inclusive.

- "search" is the desired pattern.

### Note for Marker
---

Due to the nature of the implementation printing a line everytime a new node is added, early output in terminal is usually lost as the server reads the input.

If you desire to check the entire output from the server, please redirect `stdout` to `server.log` as show in the example below. This will allow you to view all the output from the server.

Example:
```
./assignment03 -l 12345 -p happy > server.log
```

You may find `server.log` in the root directory of the assignment.


## 2. Establishing connections
The server has been designed to receive connections and input through ncat, ***in a separate shell terminal***, with the following format:
```
nc localhost <port> -d <delay> < <input_text_file>
```

Example:
```
nc localhost 12345 -d 1 < input.txt
```
In the example above,
- "localhost" is the hostname of the server.
- "12345" is the port of the server to be connected to.
- "1" is the delay in seconds between each send in chunks that the server is able to receive.
- "input.txt" is the text file being sent to the server.

### Received Output
Finally, upon complete sending of input file, the server will respond with
> Received

and the `nc` command will be done.

### Troubleshooting Connecting with NetCat:
___

*If you encounter problems with establishing a connection, please check that the server has been bound to localhost.You may check the bound host after the server has successfully started with the above-mentioned command. After which, in a separate shell terminal run the command:*

```
lsof -i :<port>
```

Example:

```
lsof -i :12345
```

This should output the hostname that your server is running on. 

Example:
```
COMMAND PID     USER    FD  TYPE    DEVICE  SIZE/OFF    NODE    NAME
python3 48505   root    3u  IPv4    219822  0t0         TCP     <hostname>:12345 (LISTEN)
```

If `<hostname>` is not `localhost`, you may use the *XXX.XX.XX.XX* format integer to establish the connection with `nc`

## 3. Testing

### File checking
Please check that the directory structure contains the following.


```
.
├── assignment3
├── assignment3.py
├── README.md
├── runTests.sh
├── tests.py
├── testServer.sh
└── test_input
    └── <Place testing .txt files here>
```

If so, proceed to the next step.

### Automated Tests
Automated tests have been provided for the following cases:

1. Starting server without any arugments.
    - Expects error message:
    ```
    Please provide a port number...
    Please provide a pattern to search...
    ```


2. Starting server without port, but with pattern.
    - Expects error message:
    ```
    Please provide a port number...
    ```

3. Starting server with port, but without pattern.
    - Expects error message:
    ```
    Please provide a pattern to search...
    ```

4. Starting server with port out of range, but with pattern.
    - Expects error message:
    ```
    Port provided is out of range.
    Valid ports include 1025 to 65535...
    ```

5. Starting server with valid port and pattern, as well as sending a valid input file.
    - Expects output message:
    ```
    Received
    ```

6. Concurrent threads to accept and process input from connections.
    - Tests for handling multiple concurrent connections.
    - Output from the test will be redirected to a logfile `multithreadTest.log`
    - Test is to be run with provided scripts, instructions below.

### Testing Instructions
Enter the following commands for the respective tests.

1. **Tests 1-5**:
    ```
    ./runBasicTests.sh > basicTests.log
    ```
    - Should be fast.
    - Refer to `basicTests.log` to check the output. (Should output True/False for each test)
<br>

2. **Test 6**:
    
    - Please place `>=10` of the UTF-8 `txt` files you wish to use for testing into `test_input` directory before proceeding.

    - The test scripts will utilise them to create an equal number of threads, creating the `nc` connections for each file.

    ```
    ./runMultithreadedTest.sh <pattern>
    ```

    Example
    ```
    ./runMultithreadedTest.sh happy
    ```
