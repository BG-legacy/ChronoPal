#!/bin/bash
# Make script executable with: chmod +x start.sh

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Install dependencies if not already installed
pip install -r requirements.txt

# Start the application
python -m gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker 