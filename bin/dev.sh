#!/bin/bash
set -e

echo "Starting Kobobo in development mode..."

# Check if settings.ini exists
if [ ! -f "src/config/settings.ini" ]; then
    echo "Error: src/config/settings.ini not found!"
    echo "Please copy src/config/settings.ini.example to src/config/settings.ini and configure it."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the application
cd src
python app.py