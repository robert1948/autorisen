#!/bin/bash

echo "🛑 Shutting down previous containers and volumes..."
docker compose down -v

echo "🔁 Rebuilding containers without cache..."
docker compose build --no-cache

echo "🚀 Starting containers in the background..."
docker compose up -d

# Wait for services to initialize
sleep 5

# Codespaces note: `xdg-open` may not work; print URL instead
APP_URL="http://localhost:8000"
echo "🌐 Your app should be live at: $APP_URL"

# Tail logs (optional, can be removed if needed)
echo "📜 Streaming container logs:"
docker compose logs -f
