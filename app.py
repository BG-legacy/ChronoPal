import sys
import os

# Add the Backend directory to the Python path
sys.path.append(os.path.abspath("Backend"))

# Import the FastAPI app
from api.main import app

# This file serves as an entry point for gunicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 