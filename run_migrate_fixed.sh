#!/bin/bash
set -euo pipefail

cd /app

if [[ -x scripts/wait_for_db.sh ]]; then
  bash scripts/wait_for_db.sh
fi

exec alembic upgrade head
