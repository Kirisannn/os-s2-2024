# OS - Assignment 03:   Multi-Threaded Network Server for Pattern Analysis


**NOTE:<br>THIS SERVER ASSUMES THAT ALL BOOKS SENT TO IT WILL BE UNIQUE, WITH UNIQUE TITLES & CONTENTS. NO BOOKS SENT TO THE SERVER WILL BE A REPEAT OF A PRE-EXISTING BOOK, OR ONE THAT HAS BEEN SENT BEFORE IN THE CURRENT RUNNING INSTANCE OF THE SERVER.**

## 1. Running the Server

To run the server, use the following command format in your shell terminal.

```
./assignment03 -l <port> -p <pattern>
```

Example:

```
./assignment03 -l 12345 -p search
```

In the example above,
- "12345" is the port desired. Valid ports range between 1025 - 65535, inclusive.

- "search" is the desired pattern.

In the interest of simplification, a Makefile has been provided with the **option "startServer"**, starting the server on **port 12345** with **pattern "basic"**.

You may run the server with that option by entering the following into your shell terminal:

```
make startServer
```

## 2. Establishing connections
The server has been designed to receive connections and input through ncat, ***in a separate shell terminal***, with the following format:
```
nc <hostname> <port> -d <delay> < <input_text_file>
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

### Troubleshooting Connecting with NetCat:
___

*If hostname is not in the format of "XXX.XX.XX.XX" such as "127.0.0.1", please start the server using the before mentioned command, then in a separate shell terminal run the command:*

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

Please copy and use that as the \<hostname\> when connecting with `nc`.

## 3. Testing

For the purposes of testing, a **directory "Part 1 Testing"** has been provided, containing test scripts for starting the server, it's error handling and sending of input.

The Structure is as follows:

```
.
├── assignment3
├── assignment3.py
├── Makefile
├── Part 1 Testing/
│   └── serverStartTests.py
│
├── input/
│   └── <insert txt files here>
│
└── README.md
```