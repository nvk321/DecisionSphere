#!/usr/bin/env bash
set -eo pipefail

echo "================================================================="
echo "  DecisionSphere — Enterprise Decision Support Platform"
echo "================================================================="

# 1. Wait for database readiness if DATABASE_URL indicates PostgreSQL
if [[ "${DATABASE_URL:-}" == *"postgres"* ]]; then
    echo "==> [DecisionSphere] Polling PostgreSQL connection readiness..."
    python - <<'EOF'
import os
import sys
import time
from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL")
if not db_url:
    sys.exit(0)

max_retries = 30
retry_delay = 2

for attempt in range(1, max_retries + 1):
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"==> [DecisionSphere] Database connectivity verified on attempt {attempt}.")
        sys.exit(0)
    except Exception as exc:
        print(f"==> [DecisionSphere] Database connection attempt {attempt}/{max_retries} pending: {exc}")
        time.sleep(retry_delay)

print("==> [DecisionSphere] ERROR: Database unavailable after 60 seconds. Aborting startup.", file=sys.stderr)
sys.exit(1)
EOF
fi

# 2. Run deterministic Alembic migrations to head
echo "==> [DecisionSphere] Running Alembic database schema migrations..."
alembic upgrade head
echo "==> [DecisionSphere] Database migrations applied successfully."

# 3. Hand off to container process (Uvicorn by default)
echo "==> [DecisionSphere] Starting application process: $@"
exec "$@"
