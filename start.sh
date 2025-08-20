#!/usr/bin/env bash
set -Eeuo pipefail

: "${PORT:=5000}"

# Run DB migrations here if needed (placeholder)
# python -m alembic upgrade head || true

# Launch Gunicorn (prod WSGI)
exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 2 --timeout 120 wsgi:app
