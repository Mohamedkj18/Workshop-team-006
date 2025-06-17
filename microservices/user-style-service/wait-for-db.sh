#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for style-db to be ready..."

while ! nc -z style-db 5432; do
  echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "Postgres is up - starting app"

exec uvicorn main:app --host 0.0.0.0 --port 8010