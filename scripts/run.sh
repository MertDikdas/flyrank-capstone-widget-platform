#!/usr/bin/env bash

set -euo pipefail

PYTHON=".venv/bin/python"
ALEMBIC=".venv/bin/alembic"

if [ ! -x "$PYTHON" ]; then
    echo "Missing .venv. Follow the README setup steps first."
    exit 1
fi

echo "Starting PostgreSQL..."
docker compose up -d db

echo "Applying database migrations..."
"$ALEMBIC" upgrade head

echo "Starting customer test site on http://localhost:5500..."
"$PYTHON" -m http.server 5500 -d customer-site > /tmp/widget-customer-site.log 2>&1 &

SITE_PID=$!

cleanup() {
    kill "$SITE_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Starting API on http://localhost:8000..."
"$PYTHON" -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000