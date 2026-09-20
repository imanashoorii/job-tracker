#!/bin/bash

set -e

echo "WAITING FOR THE DATABASE TO BE READY..."
while ! nc -z postgres 5432; do
    sleep 1
done

echo "--------DATABASE IS READY--------"

echo "RUNNING DATABASE MIGRATIONS..."
python manage.py migrate --noinput

echo "--------MIGRATION DONE--------"

echo "COLLECTING STATIC FILES..."
python manage.py collectstatic --noinput

echo "--------STATICFILES CREATION DONE--------"

echo "STARTING THE SERVER..."
exec "$@"

echo "--------SERVER STARTED--------"
