#!/bin/bash
set -e

echo "Building Kobobo Docker image..."

# Build the Docker image
docker build -f docker/Dockerfile -t kobobo:latest .

echo "Build complete! Image tagged as kobobo:latest"