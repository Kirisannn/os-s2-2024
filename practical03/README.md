# OS - Assignment 03:   Multi-Threaded Network Server for Pattern Analysis

## Assignment Objective

**To create a high-performance multi-threaded network server capable of managing incoming connections, processing text data, and analysing patterns within the data.**

### 1. Setup
- As text files required for the assignment are large, plain text(UTF-8) format books from the [Gutenberg Project](https://www.gutenberg.org) have been downloaded and used.
- Textfiles are formatted to contain the title in the first line.

#### Example Firstline
```
Title: The story of the Universe, Volume I (of 4) told by great scientists and popular authors
Editor: Esther Singleton
...
```


#### Sending Textfile to Server
- **netcat tool (nc)**  is used in the following command:
```
nc localhost <port> -i <delay> < <filename>.txt
```

- To send **Book_A.txt** to the server on **port 1024**, type the following into the shell:
```
nc localhost 1024 -i 5000 < Book_A.txt
```

### 2. Multi-Threaded Network Server
The server
- listens on **port > 1024**.
- creates a new, non-blocking thread for each incoming connection.
- handles connections from multiple clients simultaneously.
- efficiently receives and stores data in a single shared data structure (i.e. a ***list***).
- reads every line and stores it into the shared data structure - same across all threads.

## Part 1
