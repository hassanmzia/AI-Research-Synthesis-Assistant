#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null; do
    sleep 2
done
echo "PostgreSQL is ready."

# Only run migrations from the main backend container (gunicorn),
# not from celery workers/beat which also use this image.
if [ "$1" = "gunicorn" ]; then
    echo "Running makemigrations..."
    python manage.py makemigrations --noinput

    echo "Running migrations..."
    python manage.py migrate --noinput

    echo "Collecting static files..."
    python manage.py collectstatic --noinput 2>/dev/null || true
else
    # Celery containers: wait until migrations have been applied
    echo "Waiting for database migrations..."
    while ! python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT 1 FROM information_schema.tables WHERE table_name = 'django_celery_beat_periodictask'\")
assert cursor.fetchone() is not None
" 2>/dev/null; do
        sleep 3
    done
    echo "Migrations are ready."
fi

exec "$@"
