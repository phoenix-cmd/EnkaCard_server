#!/bin/bash
clear
# Load environment variables from .env file (if it exists)
if [[ -f .env ]]; then
  source .env
fi

# Get the port, prioritizing environment variables and then defaulting to 80
PORT="${PORT:-${SERVER_PORT:-80}}"

# Check if the port is a valid number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Invalid port: $PORT. Please set a valid number in .env or your environment." >&2  # Redirect to stderr
  exit 1
fi

# Define a function to start Gunicorn
start_gunicorn() {
  echo "Starting Gunicorn on port $PORT..."
  exec gunicorn main:app -b 0.0.0.0:$PORT -w 8 --timeout 600
}

# Start Gunicorn initially
start_gunicorn

# Restart loop in case of crashes
while true; do
  echo "Gunicorn exited. Restarting in 5 seconds..." >&2  # Redirect to stderr
  sleep 5
  start_gunicorn
done
