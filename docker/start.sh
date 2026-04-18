#!/usr/bin/env sh
set -eu

cd /app

# MemoryStorage FSM привязан к процессу: при 2+ воркерах состояние «Add user» теряется
# между webhook-запросами (разные процессы). Для нескольких воркеров нужен Redis FSM.
exec gunicorn admin.wsgi:application \
  --bind "0.0.0.0:${WEB_PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-1}" \
  --timeout "${WEB_TIMEOUT:-60}"

