#!/usr/bin/env sh
set -eu

cd /app

exec gunicorn admin.wsgi:application \
  --bind "0.0.0.0:${WEB_PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout "${WEB_TIMEOUT:-60}"

