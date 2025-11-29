#!/bin/bash

# CADLift dev startup (Linux/macOS, no Docker)

set -e

echo "Starting CADLift development stack (local only)..."
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup_processes() {
    echo "Cleaning up old CADLift processes..."
    if command -v pgrep >/dev/null 2>&1; then
        for pattern in "uvicorn app.main:app" "celery -A app.worker worker"; do
            pgrep -f "$pattern" >/dev/null 2>&1 && pkill -f "$pattern" && echo "  Killed: $pattern"
        done
    else
        echo "  pgrep not found; skipping cleanup"
    fi
    echo ""
}

# Ensure Python
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}Python 3 not found. Install Python 3.11+ first.${NC}"
    exit 1
fi

cd backend
cleanup_processes

# Virtualenv
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e .
else
    source .venv/bin/activate
fi
echo -e "${GREEN}Virtual environment ready.${NC}"

# Redis check
echo "Checking Redis on localhost:6379..."
start_redis() {
    if command -v redis-server >/dev/null 2>&1; then
        echo "Starting redis-server..."
        redis-server >/tmp/redis.log 2>&1 &
        sleep 2
    fi
}
if command -v nc >/dev/null 2>&1; then
    if ! nc -z localhost 6379 >/dev/null 2>&1; then
        start_redis
        if ! nc -z localhost 6379 >/dev/null 2>&1; then
            echo -e "${RED}Redis is not running. Start it locally (e.g. redis-server &).${NC}"
            exit 1
        fi
    fi
else
    python3 - <<'PY' || {
import redis, time, subprocess, shutil, os, sys
def check():
    try:
        redis.Redis(host="localhost", port=6379).ping()
        return True
    except Exception:
        return False
if not check():
    if shutil.which("redis-server"):
        subprocess.Popen(["redis-server"], stdout=open(os.devnull,"wb"), stderr=open(os.devnull,"wb"))
        time.sleep(2)
if not check():
    sys.exit(1)
PY
    if [ $? -ne 0 ]; then
        echo -e "${RED}Redis not reachable. Start redis-server.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}Redis is running.${NC}"

# Start Celery
echo "Starting Celery worker..."
.venv/bin/python -m celery -A app.worker worker --loglevel=info > ../celery.log 2>&1 &
CELERY_PID=$!
echo -e "${GREEN}Celery PID: $CELERY_PID${NC}"

# Start backend
echo "Starting FastAPI backend..."
.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}Backend PID: $BACKEND_PID${NC}"

# Health wait
echo ""
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready at http://localhost:8000${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Backend failed to start. Check backend.log.${NC}"
        kill $BACKEND_PID $CELERY_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""
echo "Services running:"
echo "  Backend PID: $BACKEND_PID (log: backend.log)"
echo "  Celery  PID: $CELERY_PID (log: celery.log)"
echo ""
echo "Stop with: kill $BACKEND_PID $CELERY_PID"
