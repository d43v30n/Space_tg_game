#!/bin/bash

# Find the PID of the running "python3 main.py" process
pid=$(ps x | grep "python3 main.py" | grep -v grep | awk '{print $1}')

if [ -z "$pid" ]; then
    echo "No process found."
else
    echo "Found process with PID: $pid"
    # Kill the process
    kill "$pid"
fi

# Remove nohup.out file
if [ -f "nohup.out" ]; then
    rm "nohup.out"
    echo "nohup.out removed."
fi

# Start "nohup python3 main.py &"
nohup python3 main.py &

echo "Started python3 main.py in the background."
