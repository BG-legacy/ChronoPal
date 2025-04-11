#!/bin/bash

# Load environment variables
set -o allexport
source .env
set +o allexport

# Export any necessary environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export PORT=${PORT:-10000}

# Print Python version and path info for debugging
echo "Python version:"
python --version
echo "Python path:"
python -c "import sys; print(sys.path)"
echo "Current directory:"
pwd
echo "Directory contents:"
ls -la

# Try to start with wsgi.py first
echo "Starting server with wsgi.py entry point..."
exec gunicorn wsgi:app \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level debug \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - 