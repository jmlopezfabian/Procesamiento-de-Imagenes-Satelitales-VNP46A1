#!/bin/bash
# Run the API server. Use this if 'uvicorn' is not in your PATH (e.g. venv not activated).
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python}"
[ -x .venv/bin/python ] && PYTHON=".venv/bin/python"
exec "$PYTHON" -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000 "$@"
