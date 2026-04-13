import os
import sys
import time

import psycopg2


def main() -> int:
    host = os.getenv("POSTGRES_HOST", "")
    if not host:
        return 0

    db = os.getenv("POSTGRES_DB", "")
    user = os.getenv("POSTGRES_USER", "")
    password = os.getenv("POSTGRES_PASSWORD", "")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    timeout_s = int(os.getenv("DB_WAIT_TIMEOUT", "60"))

    started = time.time()
    while True:
        try:
            conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=password)
            conn.close()
            return 0
        except Exception as e:
            if time.time() - started > timeout_s:
                print(f"DB not ready after {timeout_s}s: {e}", file=sys.stderr)
                return 1
            time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())

