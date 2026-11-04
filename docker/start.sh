#!/bin/sh
set -e

# Render and other platforms inject PORT; default to 8000 for local Docker.
PORT="${PORT:-8000}"

echo "Applying database migrations..."
alembic upgrade head

echo "Starting API on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
