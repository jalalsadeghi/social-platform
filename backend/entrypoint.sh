#!/bin/sh

echo "Starting migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
exec "$@"
