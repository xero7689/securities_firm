#!/bin/bash

set -e

echo "Starting entrypoint script..."

# Create logs directory if it doesn't exist
echo "Creating logs directory..."
mkdir -p logs

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --no-input

# Collect static files (if needed)
echo "Collecting static files..."
python manage.py collectstatic --no-input || echo "Static files collection failed, continuing..."

echo "Entrypoint script completed successfully!"

# Execute the main command
exec "$@"
