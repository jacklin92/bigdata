#!/bin/sh

# POA Application Entrypoint

# Collect static files
echo "Collecting static files for POA app..."
python manage.py collectstatic --noinput --clear

# Run database migrations (if needed)
echo "Running migrations for POA app..."
python manage.py migrate --noinput

# Start Gunicorn server for POA
echo "Starting Gunicorn for POA application..."
exec gunicorn website_configs.wsgi:application --bind 0.0.0.0:8000 \
  --workers 3 \
  --threads 2 \
  --timeout 30 \
  --name "poa_gunicorn"
