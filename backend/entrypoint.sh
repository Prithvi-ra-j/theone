#!/usr/bin/env bash
set -euo pipefail

# Entrypoint for the backend Docker image.
# - waits briefly for Postgres if DATABASE_URL is postgres
# - runs alembic migrations
# - starts uvicorn

echo "Starting backend entrypoint..."

if [[ -z "${PORT:-}" ]]; then
  PORT=8000
fi

if [[ "${DATABASE_URL:-}" == postgresql* ]]; then
  echo "Detected postgres DATABASE_URL, waiting for DB to be ready..."
  # Parse host and port (simple heuristic)
  # If pg_isready is available, use it; otherwise sleep a bit to let service come up
  if command -v pg_isready >/dev/null 2>&1; then
    for i in {1..30}; do
      if pg_isready -q; then
        echo "Postgres is ready"
        break
      fi
      echo "Waiting for Postgres... ($i)"
      sleep 1
    done
  else
    echo "pg_isready not available; sleeping 3s"
    sleep 3
  fi
fi

echo "Running alembic upgrade head..."
alembic upgrade head

echo "Starting uvicorn on port ${PORT}"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers
