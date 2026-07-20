#!/bin/sh

set -e

echo "Running migrations..."
python manage.py migrate

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Seeding database..."
python manage.py seed_db


echo "Starting server..."
exec "$@"