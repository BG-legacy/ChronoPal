from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import List, Optional, Union, Dict
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from .pet_schema import Pet, MOOD_LEVELS, SASS_LEVELS, NEGLECT_THRESHOLD_HOURS
from .user_schema import User, UserCreate
from passlib.context import CryptContext
from bson import ObjectId

# Load environment variables
load_dotenv()

# MongoDB connection string and database name
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

if not MONGODB_URI or not DB_NAME:
    raise ValueError("MongoDB connection settings are not properly configured in environment variables")

# Initialize MongoDB client with simplified SSL settings
client = MongoClient(MONGODB_URI, 
                    connectTimeoutMS=30000, 
                    socketTimeoutMS=30000,
                    serverSelectionTimeoutMS=5000,
                    retryWrites=True,
                    w="majority")

# Test the connection
try:
    client.server_info()
except Exception as e:
    raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

db = client[DB_NAME]
pets_collection = db["pets"]
users_collection = db["users"]

# Async client for FastAPI with simplified SSL settings
async_client = AsyncIOMotorClient(MONGODB_URI, 
                                 connectTimeoutMS=30000, 
                                 socketTimeoutMS=30000,
                                 serverSelectionTimeoutMS=5000,
                                 retryWrites=True,
                                 w="majority")

async_db = async_client[DB_NAME]
async_pets_collection = async_db["pets"]
async_users_collection = async_db["users"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy logger for demonstration; replace with actual log_memory implementation
async def log_memory(pet_id: str, action_type: str, message: str):
    print(f"[MEMORY LOG] Pet ID: {pet_id} | Action: {action_type} | Message: {message}")

# ... rest of the UserDB and PetDB class remain unchanged until feed_pet, play_with_pet, teach_pet

class PetDB:
    # other static methods omitted for brevity

    @staticmethod
    async def feed_pet(pet_id: str) -> Optional[Pet]:
        try:
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None

            battery_level = getattr(pet, 'batteryLevel', 100)
            if battery_level is not None and battery_level <= 0:
                return pet

            now = datetime.now(timezone.utc)
            updates = {
                "lastFed": now,
                "lastInteraction": now,
                "mood": MOOD_LEVELS["HAPPY"]
            }

            await PetDB.update_battery_level(pet_id, 10)
            await PetDB.increment_interaction(pet_id)
            await PetDB.add_memory(pet_id, "I was fed and it was delicious!")
            await log_memory(pet_id, "feed", "Pet was fed and is happy.")

            return await PetDB.update_pet(pet_id, updates)
        except Exception as e:
            print(f"Error feeding pet: {str(e)}")
            return None

    @staticmethod
    async def play_with_pet(pet_id: str) -> Optional[Pet]:
        try:
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None

            battery_level = getattr(pet, 'batteryLevel', 100)
            if battery_level is not None and battery_level <= 0:
                return pet

            now = datetime.now(timezone.utc)
            updates = {
                "lastInteraction": now,
                "mood": MOOD_LEVELS["HAPPY"]
            }

            await PetDB.update_battery_level(pet_id, 5)
            await PetDB.increment_interaction(pet_id)
            await PetDB.add_memory(pet_id, "We played together and it was fun!")
            await log_memory(pet_id, "play", "Pet played and felt joy.")

            return await PetDB.update_pet(pet_id, updates)
        except Exception as e:
            print(f"Error playing with pet: {str(e)}")
            return None

    @staticmethod
    async def teach_pet(pet_id: str, lesson: str) -> Optional[Pet]:
        try:
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None

            battery_level = getattr(pet, 'batteryLevel', 100)
            if battery_level is not None and battery_level <= 0:
                return pet

            now = datetime.now(timezone.utc)
            updates = {
                "lastInteraction": now,
                "level": pet.level + 1
            }

            await PetDB.update_battery_level(pet_id, 7)
            await PetDB.increment_interaction(pet_id)
            await PetDB.add_memory(pet_id, f"I learned about {lesson}")
            await log_memory(pet_id, "teach", f"Pet learned a lesson on {lesson}.")

            return await PetDB.update_pet(pet_id, updates)
        except Exception as e:
            print(f"Error teaching pet: {str(e)}")
            return None
