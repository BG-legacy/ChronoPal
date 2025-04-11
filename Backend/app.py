import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import app

# This file serves as the entry point for Gunicorn
# No additional code needed as we're just importing and exposing the app 