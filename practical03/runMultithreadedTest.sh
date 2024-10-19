#!/bin/bash

pattern=$1

./testMultithreadServer.sh $pattern > multithread.log &

python multithreadTest.py --port 12345 > multithreadTest.log 

# Combine the log files
echo "===========================================================================" >> multithreadTest.log
cat multithread.log >> multithreadTest.log

kill $(lsof -t -i :12345)

rm multithread.log
rm *.txt