import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection string from environment variable
MONGODB_URI = os.getenv("MONGODB_URI")

# Initialize the MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

# Get the 'chronopal' database
db = client.chronopal