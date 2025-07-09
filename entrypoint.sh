#!/bin/bash

set -e

echo "Starting entrypoint script..."

# Wait for database to be ready
# echo "Waiting for database to be ready..."
#while ! python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; do
#    echo "Database not ready, waiting 2 seconds..."
#    sleep 2
#done

#echo "Database is ready!"

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --no-input

# Collect static files (if needed)
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear || echo "Static files collection failed, continuing..."

echo "Entrypoint script completed successfully!"

# Execute the main command
exec "$@"
