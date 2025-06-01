#!/bin/bash

for PORT in 3000 8000
do
  PID=$(lsof -t -i:$PORT)
  if [ -n "$PID" ]; then
    echo "Killing process on port $PORT (PID $PID)..."
    kill -9 $PID
  else
    echo "No process on port $PORT"
  fi
done
