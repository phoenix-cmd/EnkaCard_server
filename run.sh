#!/bin/bash

# Load environment variables from .env file (if it exists)
if [[ -f .env ]]; then
  source .env
fi

# Get the port, prioritizing environment variables and then defaulting to 80
PORT="${PORT:-${SERVER_PORT:-80}}"  

# Check if the port is a valid number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Invalid port: $PORT. Please set a valid number in .env or your environment."
  exit 1
fi

# Run Gunicorn
echo "Starting Gunicorn on port $PORT..."
gunicorn main:app -b 0.0.0.0:$PORT -w 8