#!/bin/sh
set -e
echo "Waiting for DB..."
python -c "
import time
from sqlalchemy import create_engine, text
from app.core.config import get_settings
url = get_settings().DATABASE_URL
for i in range(30):
    try:
        e = create_engine(url)
        with e.connect() as c:
            c.execute(text('SELECT 1'))
        break
    except Exception:
        time.sleep(1)
else:
    exit(1)
"
echo "Running migrations..."
alembic upgrade head
echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
