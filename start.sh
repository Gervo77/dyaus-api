#!/bin/sh
PORT="${PORT:-8080}"
echo "Starting Dyaus API on port $PORT"
exec gunicorn app:app --bind "0.0.0.0:$PORT" --timeout 120 --workers 2
