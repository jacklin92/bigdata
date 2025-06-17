#!/bin/sh

# LLM Application Entrypoint

# Collect static files
echo "Collecting static files for LLM app..."
python manage.py collectstatic --noinput --clear

# Run database migrations (if needed)
# echo "Running migrations for LLM app..."
# python manage.py migrate --noinput

# Start Gunicorn server for LLM
echo "Starting Gunicorn for LLM application..."
exec gunicorn website_configs.wsgi:application --bind 0.0.0.0:8001 \
  --workers 2 \
  --threads 2 \
  --timeout 60 \
  --name "llm_gunicorn"
