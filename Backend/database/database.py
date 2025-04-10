from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from .pet_schema import Pet

# Load environment variables
load_dotenv()

# MongoDB connection string and database name
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
pets_collection = db["pets"]

# Async client for FastAPI
async_client = AsyncIOMotorClient(MONGODB_URI)
async_db = async_client[DB_NAME]
async_pets_collection = async_db["pets"]

class PetDB:
    @staticmethod
    async def create_pet(pet: Pet) -> Pet:
        pet_dict = pet.model_dump(by_alias=True)
        result = await async_pets_collection.insert_one(pet_dict)
        created_pet = await async_pets_collection.find_one({"_id": result.inserted_id})
        return Pet(**created_pet)

    @staticmethod
    async def get_pet(pet_id: str) -> Optional[Pet]:
        pet = await async_pets_collection.find_one({"_id": pet_id})
        return Pet(**pet) if pet else None

    @staticmethod
    async def get_pets_by_user(user_id: str) -> List[Pet]:
        pets = await async_pets_collection.find({"userId": user_id}).to_list(length=None)
        return [Pet(**pet) for pet in pets]

    @staticmethod
    async def update_pet(pet_id: str, pet_data: dict) -> Optional[Pet]:
        # Remove None values from update data
        update_data = {k: v for k, v in pet_data.items() if v is not None}
        
        if update_data:
            await async_pets_collection.update_one(
                {"_id": pet_id},
                {"$set": update_data}
            )
        
        updated_pet = await async_pets_collection.find_one({"_id": pet_id})
        return Pet(**updated_pet) if updated_pet else None

    @staticmethod
    async def delete_pet(pet_id: str) -> bool:
        result = await async_pets_collection.delete_one({"_id": pet_id})
        return result.deleted_count > 0

    @staticmethod
    async def add_memory(pet_id: str, memory: str) -> Optional[Pet]:
        await async_pets_collection.update_one(
            {"_id": pet_id},
            {"$push": {"memoryLog": memory}}
        )
        updated_pet = await async_pets_collection.find_one({"_id": pet_id})
        return Pet(**updated_pet) if updated_pet else None

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
        return await PetDB.update_pet(pet_id, {"lastFed": datetime.utcnow()}) 