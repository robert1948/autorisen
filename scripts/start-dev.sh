#!/bin/bash

echo "🔍 Checking for processes on ports 3000 and 8000..."

for PORT in 3000 8000
do
  PID=$(lsof -t -i:$PORT)
  if [ -n "$PID" ]; then
    echo "⚠️  Port $PORT in use by PID $PID. Killing it..."
    kill -9 $PID
  else
    echo "✅ Port $PORT is free."
  fi
done

echo "✅ Starting backend..."
cd backend
source ../venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "✅ Starting frontend..."
cd client
npm install
npm start &

echo "🟢 Dev environment is now live."
echo "🔁 Backend PID: $BACKEND_PID"
