#!/bin/bash

echo "$DISABLE_LOCAL_OLLAMA"

DISABLE_VENV="${DISABLE_VENV:-0}"
DISABLE_LOCAL_OLLAMA="${DISABLE_LOCAL_OLLAMA:-0}"

RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'

if [ "$DISABLE_VENV" -eq 1 ]; then
    echo "  .venv disabled"
else
    echo "  .venv enabled"
    python3 -m venv .venv
    source .venv/bin/activate
fi

echo "Installing current package..."
if ! pip install -e . 2>logs/init.log; then
    echo "Failed to install the package in editable mode."
    printf "Error log: %s" "$RED"
    cat logs/init.log
    echo -e "$RESET Please check the setup and consider manually removing and recreating .venv if needed:"
    echo -e "$CYAN    rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate $RESET"
    exit 1
fi

if [ ! -f .env.localhost ]; then
  cp .env.localhost.example .env.localhost
fi

set -a; source .env.localhost; set +a

if [ "$DISABLE_LOCAL_OLLAMA" -eq 1 ]; then
  echo "Local Ollama disabled by env \`DISABLE_LOCAL_OLLAMA=$DISABLE_LOCAL_OLLAMA\`"
  echo "External Ollama should be listening on OLLAMA_HOST=$OLLAMA_HOST"
else
  echo "Starting Ollama Server"
  ollama serve &

  echo "Pulling LLama3.1 model"
  ollama pull llama3.1

  echo "Pulling LLama3.2-vision model"
  ollama pull llama3.2-vision
fi

echo "Starting Redis"

echo "Your ENV settings loaded from .env.localhost file: "
printenv

CELERY_BIN="$(pwd)/.venv/bin/celery"
CELERY_PIDS=$(pgrep -f "$CELERY_BIN")

if [ -n "$CELERY_PIDS" ]; then
  echo "Killing existing Celery processes from $CELERY_BIN with PIDs:"
  echo "$CELERY_PIDS"
  for PID in $CELERY_PIDS; do
    kill "$PID" || echo "Failed to kill process with PID: $PID"
  done
else
  echo "No running Celery process found."
fi

REDIS_PORT=6379 # will move it to .envs in near future

if lsof -i :$REDIS_PORT | grep LISTEN >/dev/null; then
  echo "Redis is already running on port $REDIS_PORT. Skipping Redis start."
else
  echo "Starting Redis..."
  docker run -p $REDIS_PORT:6379 --restart always --detach redis &
fi


echo "Starting Celery Worker and FastAPI server"
if [ $APP_ENV = 'production' ]; then
    celery -A text_extract_api.celery_init worker --loglevel=info --pool=solo & # to scale by concurrent processing please run this line as many times as many concurrent processess you want to have running; keep in mind that after next run they will be killed
    uvicorn text_extract_api.main:app --host 0.0.0.0 --port 8000;
else

  trap 'kill $(jobs -p) && exit' SIGINT SIGTERM
  (
      "$CELERY_BIN" -A text_extract_api.celery_app worker --loglevel=debug --pool=solo &
      uvicorn text_extract_api.main:app --host 0.0.0.0 --port 8000 --reload
  )
fi
