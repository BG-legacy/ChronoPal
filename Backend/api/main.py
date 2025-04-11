from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a global sessions dictionary that will persist between requests
# In production, use Redis or another persistent store
if 'ACTIVE_SESSIONS' not in globals():
    print("Initializing global session storage")
    global ACTIVE_SESSIONS
    ACTIVE_SESSIONS = {}

# Share the global sessions with the routes module
from api.routes import set_active_sessions
set_active_sessions(ACTIVE_SESSIONS)

app = FastAPI(
    title="ChronoPal API",
    description="API for ChronoPal virtual pet application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router, prefix="/api") 