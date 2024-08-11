#!/bin/bash

# Search for even and kill
evenPID=$(ps -au | grep "./even 5" | grep -v grep | awk '{print $2}') 

sigHup="HUP"
sigInt="INT"

kill -$sigHup $evenPID
sleep 4
kill -$sigInt $evenPID