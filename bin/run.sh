#!/bin/bash
set -e

# Default environment variables (can be overridden)
KOBOBO_CALIBRE_URL=${KOBOBO_CALIBRE_URL:-"http://192.168.1.100:8090"}
KOBOBO_USERNAME=${KOBOBO_USERNAME:-"admin"}
KOBOBO_PASSWORD=${KOBOBO_PASSWORD:-"admin"}
KOBOBO_PORT=${KOBOBO_PORT:-"5055"}

echo "Starting Kobobo Docker container..."
echo "Calibre URL: $KOBOBO_CALIBRE_URL"
echo "Port: $KOBOBO_PORT"

# Run the Docker container
docker run --rm -it \
  -p "$KOBOBO_PORT:5055" \
  -e KOBOBO_CALIBRE_URL="$KOBOBO_CALIBRE_URL" \
  -e KOBOBO_USERNAME="$KOBOBO_USERNAME" \
  -e KOBOBO_PASSWORD="$KOBOBO_PASSWORD" \
  kobobo:latest

echo "Container stopped."