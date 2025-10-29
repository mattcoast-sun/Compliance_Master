#!/bin/bash

# Compliance Master API - Run Script

echo "Starting Compliance Master API..."
echo "================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create a .env file with your WatsonX credentials."
    echo "See README.md for details."
    exit 1
fi

# Run the application
echo "Starting server on http://0.0.0.0:8765"
echo "API Documentation: http://localhost:8765/docs"
echo "================================="
uvicorn main:app --reload --reload-exclude 'venv/*' --host 0.0.0.0 --port 8765

