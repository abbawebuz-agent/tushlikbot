#!/usr/bin/env sh
set -eu

cd /app

python /app/docker/wait_for_postgres.py
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

