#!/bin/sh
set -e

echo "Waiting for database..."
python -c "from app.core.db_check import wait_for_db; exit(0 if wait_for_db() else 1)"

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
