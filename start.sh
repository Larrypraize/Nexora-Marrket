#!/usr/bin/env bash
# ============================================================
# NEXORA MARKET — one-command launcher
# Starts the backend, which ALSO serves the website.
# Open the printed URL in your browser.
# ============================================================
set -e
cd "$(dirname "$0")/backend"

# create venv on first run
if [ ! -d ".venv" ]; then
  echo "→ Creating virtual environment & installing dependencies (first run)..."
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
fi

# default env (mock data) if none provided
if [ ! -f .env ]; then
  echo "→ No .env found — copying .env.example (runs with demo/mock data)."
  cp .env.example .env
fi

PORT="${PORT:-8000}"
echo ""
echo "============================================================"
echo "  NEXORA MARKET is starting..."
echo ""
echo "    🌐  Website : http://localhost:${PORT}/"
echo "    📚  API docs: http://localhost:${PORT}/docs"
echo "    ❤️  Health  : http://localhost:${PORT}/health"
echo ""
echo "  (Add real API keys in backend/.env for live market data.)"
echo "============================================================"
echo ""

exec ./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
