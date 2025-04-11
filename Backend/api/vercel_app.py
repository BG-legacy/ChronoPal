from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import os
from dotenv import load_dotenv
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

# Load environment variables
load_dotenv()

# MongoDB connection with connection pooling optimized for serverless
# Create a cached connection to MongoDB
mongo_client = None

def get_mongo_client():
    global mongo_client
    if mongo_client is None:
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable not set")
        
        # Configure connection pooling for serverless environment
        # Set minimal pooling with quick timeouts
        mongo_client = AsyncIOMotorClient(
            mongodb_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=10,
            minPoolSize=0,
            maxIdleTimeMS=50000
        )
    return mongo_client

# Create a global sessions dictionary that will persist between requests
# In production, use MongoDB to store sessions
if 'ACTIVE_SESSIONS' not in globals():
    print("Initializing global session storage")
    global ACTIVE_SESSIONS
    ACTIVE_SESSIONS = {}

# Share the global sessions with the routes module
from api.routes import set_active_sessions, set_mongo_client
set_active_sessions(ACTIVE_SESSIONS)
set_mongo_client(get_mongo_client)

app = FastAPI(
    title="ChronoPal API",
    description="API for ChronoPal virtual pet application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chrono-pal.vercel.app", "http://localhost:3000"],  # Production and local development URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router, prefix="/api") 