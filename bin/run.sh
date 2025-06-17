#!/bin/bash
set -e

# Check if kobobo.yml exists
if [ ! -f "kobobo.yml" ]; then
    echo "Error: kobobo.yml not found in current directory!"
    echo "This file contains the configuration for the Kobobo service."
    exit 1
fi

# Extract values from kobobo.yml using basic parsing
KOBOBO_CALIBRE_URL=$(grep "KOBOBO_CALIBRE_URL:" kobobo.yml | sed 's/.*KOBOBO_CALIBRE_URL: *//')
KOBOBO_USERNAME=$(grep "KOBOBO_USERNAME:" kobobo.yml | sed 's/.*KOBOBO_USERNAME: *//')
KOBOBO_PASSWORD=$(grep "KOBOBO_PASSWORD:" kobobo.yml | sed 's/.*KOBOBO_PASSWORD: *//')
KOBOBO_PORT=$(grep -A1 "ports:" kobobo.yml | grep -o '"[0-9]*:' | cut -d'"' -f2 | cut -d':' -f1)
# If port is 5057 in yml, use that for external mapping
EXTERNAL_PORT=${KOBOBO_PORT:-"5055"}

# Use defaults if not found in yml
KOBOBO_PORT=${KOBOBO_PORT:-"5055"}

echo "Starting Kobobo Docker container..."
echo "Reading configuration from kobobo.yml:"
echo "Calibre URL: $KOBOBO_CALIBRE_URL"
echo "Username: $KOBOBO_USERNAME" 
echo "Port: $KOBOBO_PORT"

# Run the Docker container with mounted kobobo.yml
echo "Starting container in background..."
CONTAINER_ID=$(docker run --rm -d \
  -p "$EXTERNAL_PORT:5055" \
  -v "$(pwd)/kobobo.yml:/app/kobobo.yml:ro" \
  -e KOBOBO_CALIBRE_URL="$KOBOBO_CALIBRE_URL" \
  -e KOBOBO_USERNAME="$KOBOBO_USERNAME" \
  -e KOBOBO_PASSWORD="$KOBOBO_PASSWORD" \
  kobobo:latest)

echo "Container started with ID: $CONTAINER_ID"
echo "Waiting for startup..."
sleep 3

# Check if container is still running
if docker ps --format "{{.ID}}" | grep -q "${CONTAINER_ID:0:12}"; then
    echo "✅ Container is running successfully"
    echo "🌐 Web interface available at: http://localhost:$EXTERNAL_PORT"
    echo "📊 Debug info at: http://localhost:$EXTERNAL_PORT/debug/series"
    echo ""
    echo "To view logs: docker logs $CONTAINER_ID"
    echo "To stop: docker stop $CONTAINER_ID"
else
    echo "❌ Container failed to start. Checking logs..."
    docker logs "$CONTAINER_ID" 2>/dev/null || echo "No logs available"
fi