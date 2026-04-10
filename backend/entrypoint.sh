#!/bin/sh
set -eu

# If DB_HOST is provided, wait for PostgreSQL to be reachable.
if [ -n "${DB_HOST:-}" ]; then
  python - <<'PY'
import os
import socket
import time

host = os.environ.get("DB_HOST")
port = int(os.environ.get("DB_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("PostgreSQL is reachable")
            break
    except OSError:
        time.sleep(2)
else:
    raise SystemExit("PostgreSQL is not reachable after waiting")
PY
fi

python manage.py migrate --noinput
exec daphne -b 0.0.0.0 -p 8001 backend.asgi:application
