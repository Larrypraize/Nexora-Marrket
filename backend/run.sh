#!/usr/bin/env bash
# Start the NEXORA MARKET backend (development)
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "→ No .env found, copying .env.example (mock mode)."
  cp .env.example .env
fi

python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
