#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# ComicCraft AI — Automatic Port Killer & Startup Script
# ─────────────────────────────────────────────────────────────

PORT=8000

echo "🔍 Checking for existing processes on port $PORT..."
fuser -k ${PORT}/tcp 2>/dev/null || true
sleep 1

# Activate virtual environment
if [ -d "env" ]; then
    source env/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "🚀 Starting ComicCraft AI on http://127.0.0.1:${PORT} ..."
exec python -m uvicorn app.main:app --reload --host 127.0.0.1 --port ${PORT}
