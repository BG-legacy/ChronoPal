from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router, set_mongo_client
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from datetime import datetime, timedelta
from database.database import get_client, set_mongo_client as set_db_client

# Load environment variables
load_dotenv()

# Initialize MongoDB client
async def initialize_mongodb():
    try:
        client = await get_client()
        set_db_client(client)  # Set the global client in database.py
        set_mongo_client(lambda: client)  # Set the client function in routes.py
        print("MongoDB client initialized successfully")
        return client
    except Exception as e:
        print(f"Error initializing MongoDB: {str(e)}")
        raise

# Session management using MongoDB
async def get_session(session_id: str):
    client = await get_client()
    db = client[os.getenv("MONGODB_DB_NAME", "chronopal")]
    session = await db.sessions.find_one({"session_id": session_id})
    if session and datetime.now() < session["expires_at"]:
        return session
    return None

async def create_session(user_id: str):
    client = await get_client()
    db = client[os.getenv("MONGODB_DB_NAME", "chronopal")]
    session_id = os.urandom(16).hex()
    expires_at = datetime.now() + timedelta(days=1)
    await db.sessions.insert_one({
        "session_id": session_id,
        "user_id": user_id,
        "expires_at": expires_at
    })
    return session_id

async def delete_session(session_id: str):
    client = await get_client()
    db = client[os.getenv("MONGODB_DB_NAME", "chronopal")]
    await db.sessions.delete_one({"session_id": session_id})

# Share the session management functions with the routes module
from api.routes import set_session_functions
set_session_functions({
    "get_session": get_session,
    "create_session": create_session,
    "delete_session": delete_session
})

app = FastAPI(
    title="ChronoPal API",
    description="API for ChronoPal virtual pet application",
    version="1.0.0"
)

# Configure CORS - Allow both local and Heroku domains
allowed_origins = [
    "http://localhost:3000",  # Local development URL
    "http://localhost:8000",  # Local backend URL
    "https://chronopal-backend-00ae6a240df5.herokuapp.com",  # Backend URL
    "https://chrono-pal.vercel.app",  # Production frontend URL
    "https://chrono-pal-git-main-bginnjr20.vercel.app",  # Vercel deployment URL
]

# Allow all origins in development mode (optional)
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB on startup
@app.on_event("startup")
async def startup_event():
    await initialize_mongodb()

# Include the router
app.include_router(router, prefix="/api") 