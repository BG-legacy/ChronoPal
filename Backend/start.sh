#!/bin/bash

# Load environment variables
source .env

# Export any necessary environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start Gunicorn with our configuration
exec gunicorn -c gunicorn_config.py api.main:app 