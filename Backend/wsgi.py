#!/usr/bin/env python
# This file serves as the entry point for Render deployment

# Import the FastAPI app from api.main
import os
import sys

# Add the current directory to the path so Python can find the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import app

# This allows the application to be imported by Gunicorn
# The app object is what Gunicorn expects to find
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("wsgi:app", host="0.0.0.0", port=int(os.getenv("PORT", "10000")), log_level="info") 