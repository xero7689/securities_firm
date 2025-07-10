#!/bin/bash

set -e

echo "Starting entrypoint script..."

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --no-input

# Collect static files (if needed)
echo "Collecting static files..."
python manage.py collectstatic --no-input || echo "Static files collection failed, continuing..."

# Start uvicorn directly (no exec "$@")
WORKER_COUNT=${UVICORN_WORKER_NUMS:-1}
if [ "$UVICORN_DEBUG_RELOAD" = "true" ]; then
  echo "Starting uvicorn with DEBUG_RELOAD"
  exec python -m uvicorn securities_firm.asgi:application \
      --host 0.0.0.0 \
      --port 8080 \
      --reload
fi

  echo "Starting uvicorn with ${WORKER_COUNT} workers..."
  exec python -m uvicorn securities_firm.asgi:application \
      --host 0.0.0.0 \
      --port 8080 \
      --workers ${WORKER_COUNT}
