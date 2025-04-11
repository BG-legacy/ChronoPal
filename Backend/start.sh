#!/bin/bash

# Load environment variables
set -o allexport
source .env
set +o allexport

# Export any necessary environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export PORT=${PORT:-10000}

# Start Gunicorn with the wsgi.py entry point
exec gunicorn wsgi:app \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level info \
    --access-logfile - \
    --error-logfile - 