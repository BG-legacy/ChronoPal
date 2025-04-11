from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import certifi

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variables
# Heroku will set MONGODB_URI or DATABASE_URL automatically if you use an add-on
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("DATABASE_URL")
DB_NAME = os.getenv("MONGODB_DB_NAME")

if not MONGODB_URI:
    raise ValueError("MongoDB URI not found in environment variables")
if not DB_NAME:
    raise ValueError("MongoDB database name not found in environment variables")

# Function to get database connection
async def get_database():
    client = AsyncIOMotorClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        maxPoolSize=10,
        minPoolSize=0,
        maxIdleTimeMS=50000,
        tlsCAFile=certifi.where()
    )
    return client[DB_NAME]

# Function to close database connection
async def close_database(client):
    client.close() 