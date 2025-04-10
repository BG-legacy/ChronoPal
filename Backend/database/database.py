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

# Initialize MongoDB client with simplified SSL settings
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000, socketTimeoutMS=30000)
db = client[DB_NAME]
pets_collection = db["pets"]
users_collection = db["users"]

# Async client for FastAPI with simplified SSL settings
async_client = AsyncIOMotorClient(MONGODB_URI, connectTimeoutMS=30000, socketTimeoutMS=30000)
async_db = async_client[DB_NAME]
async_pets_collection = async_db["pets"]
async_users_collection = async_db["users"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserDB:
    @staticmethod
    async def create_user(user: UserCreate) -> User:
        hashed_password = UserDB.get_password_hash(user.password)
        user_dict = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc)
        }
        result = await async_users_collection.insert_one(user_dict)
        created_user = await async_users_collection.find_one({"_id": result.inserted_id})
        if created_user:
            created_user["_id"] = str(created_user["_id"])
        return User(**created_user)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        user = await async_users_collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return User(**user) if user else None

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        try:
            user = await async_users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return User(**user) if user else None
        except:
            return None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        try:
            result = await async_users_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False

class PetDB:
    @staticmethod
    async def create_pet(pet_data: Union[Pet, Dict]) -> Pet:
        """Create a new pet from either a Pet object or a dictionary"""
        try:
            if isinstance(pet_data, dict):
                # If it's a dictionary, create a Pet object
                pet = Pet(**pet_data)
                pet_dict = pet.model_dump(by_alias=True)
            else:
                # If it's already a Pet object, just get the dictionary
                pet_dict = pet_data.model_dump(by_alias=True)

            # Remove _id if it exists to let MongoDB generate it
            if "_id" in pet_dict:
                del pet_dict["_id"]

            result = await async_pets_collection.insert_one(pet_dict)
            created_pet = await async_pets_collection.find_one({"_id": result.inserted_id})
            if created_pet:
                created_pet["_id"] = str(created_pet["_id"])
            return Pet(**created_pet)
        except Exception as e:
            print(f"Error creating pet: {str(e)}")
            raise

    @staticmethod
    async def get_pet(pet_id: str) -> Optional[Pet]:
        try:
            pet = await async_pets_collection.find_one({"_id": ObjectId(pet_id)})
            if pet:
                pet["_id"] = str(pet["_id"])
            return Pet(**pet) if pet else None
        except:
            return None

    @staticmethod
    async def get_pets_by_user(user_id: str) -> List[Pet]:
        pets = await async_pets_collection.find({"userId": user_id}).to_list(length=None)
        for pet in pets:
            pet["_id"] = str(pet["_id"])
        return [Pet(**pet) for pet in pets]

    @staticmethod
    async def update_pet(pet_id: str, pet_data: dict) -> Optional[Pet]:
        try:
            # Remove None values from update data
            update_data = {k: v for k, v in pet_data.items() if v is not None}
            
            if update_data:
                await async_pets_collection.update_one(
                    {"_id": ObjectId(pet_id)},
                    {"$set": update_data}
                )
            
            updated_pet = await async_pets_collection.find_one({"_id": ObjectId(pet_id)})
            if updated_pet:
                updated_pet["_id"] = str(updated_pet["_id"])
            return Pet(**updated_pet) if updated_pet else None
        except:
            return None

    @staticmethod
    async def delete_pet(pet_id: str) -> bool:
        try:
            result = await async_pets_collection.delete_one({"_id": ObjectId(pet_id)})
            return result.deleted_count > 0
        except:
            return False

    @staticmethod
    async def add_memory(pet_id: str, memory: str) -> Optional[Pet]:
        try:
            await async_pets_collection.update_one(
                {"_id": ObjectId(pet_id)},
                {"$push": {"memoryLog": memory}}
            )
            updated_pet = await async_pets_collection.find_one({"_id": ObjectId(pet_id)})
            if updated_pet:
                updated_pet["_id"] = str(updated_pet["_id"])
            return Pet(**updated_pet) if updated_pet else None
        except:
            return None

    @staticmethod
    async def update_mood(pet_id: str, mood: str) -> Optional[Pet]:
        return await PetDB.update_pet(pet_id, {"mood": mood})

    @staticmethod
    async def update_level(pet_id: str, level: int) -> Optional[Pet]:
        return await PetDB.update_pet(pet_id, {"level": level})

    @staticmethod
    async def update_evolution_stage(pet_id: str, stage: str) -> Optional[Pet]:
        return await PetDB.update_pet(pet_id, {"evolutionStage": stage})

    @staticmethod
    async def update_last_fed(pet_id: str) -> Optional[Pet]:
        return await PetDB.update_pet(pet_id, {"lastFed": datetime.now(timezone.utc)})

    @staticmethod
    async def update_last_interaction(pet_id: str) -> Optional[Pet]:
        """Update the last interaction timestamp"""
        return await PetDB.update_pet(pet_id, {"lastInteraction": datetime.now(timezone.utc)})

    @staticmethod
    async def check_neglect(pet_id: str) -> Optional[Pet]:
        """Check if pet has been neglected and update state accordingly"""
        pet = await PetDB.get_pet(pet_id)
        if not pet:
            return None

        now = datetime.now(timezone.utc)
        # Ensure lastInteraction is timezone-aware
        if pet.lastInteraction.tzinfo is None:
            pet.lastInteraction = pet.lastInteraction.replace(tzinfo=timezone.utc)
        
        hours_since_interaction = (now - pet.lastInteraction).total_seconds() / 3600

        if hours_since_interaction > NEGLECT_THRESHOLD_HOURS:
            # Calculate how many neglect periods have passed
            neglect_periods = int(hours_since_interaction / NEGLECT_THRESHOLD_HOURS)
            
            # Calculate new sass level based on neglect periods
            # For 3 or more neglect periods, increase by 2 levels
            # For 1-2 neglect periods, increase by 1 level
            sass_increase = 2 if neglect_periods >= 3 else 1
            new_sass_level = min(pet.sass_level + sass_increase, SASS_LEVELS["SAVAGE"])
            
            # Update pet state based on neglect
            updates = {
                "mood": MOOD_LEVELS["GRUMPY"],
                "sass_level": new_sass_level,
                "level": max(pet.level - neglect_periods, 1)
            }
            
            # Add a memory about being neglected
            memory = f"Pet was neglected for {int(hours_since_interaction)} hours"
            await PetDB.add_memory(pet_id, memory)
            
            return await PetDB.update_pet(pet_id, updates)
        
        return pet

    @staticmethod
    async def increment_interaction(pet_id: str) -> Optional[Pet]:
        """Increment interaction count and potentially update sass level"""
        # First check for neglect
        await PetDB.check_neglect(pet_id)
        
        pet = await PetDB.get_pet(pet_id)
        if not pet:
            return None
            
        new_interaction_count = pet.interactionCount + 1
        new_sass_level = pet.sass_level
        
        # Update sass level based on interaction milestones
        if new_interaction_count >= 100 and pet.sass_level < SASS_LEVELS["SAVAGE"]:
            new_sass_level = SASS_LEVELS["SAVAGE"]
        elif new_interaction_count >= 50 and pet.sass_level < SASS_LEVELS["SASSY"]:
            new_sass_level = SASS_LEVELS["SASSY"]
        elif new_interaction_count >= 25 and pet.sass_level < SASS_LEVELS["SNARKY"]:
            new_sass_level = SASS_LEVELS["SNARKY"]
        elif new_interaction_count >= 10 and pet.sass_level < SASS_LEVELS["PLAYFUL"]:
            new_sass_level = SASS_LEVELS["PLAYFUL"]
            
        return await PetDB.update_pet(pet_id, {
            "interactionCount": new_interaction_count,
            "sass_level": new_sass_level,
            "lastInteraction": datetime.now(timezone.utc)
        })

    @staticmethod
    async def get_sass_level(pet_id: str) -> Optional[int]:
        """Get the current sass level of a pet"""
        pet = await PetDB.get_pet(pet_id)
        return pet.sass_level if pet else None 