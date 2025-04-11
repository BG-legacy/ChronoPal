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
                pet_dict = pet.model_dump()
            else:
                # If it's already a Pet object, just get the dictionary
                pet_dict = pet_data.model_dump()

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
            print(f"[DEBUG] Looking for pet with ID: {pet_id}")
            print(f"[DEBUG] Pet ID type: {type(pet_id)}")
            print(f"[DEBUG] Pet ID value: {pet_id}")
            
            # Dump the first few pets in the collection for debugging
            print(f"[DEBUG] Dumping first 3 pets in collection:")
            cursor = async_pets_collection.find().limit(3)
            idx = 0
            async for pet in cursor:
                idx += 1
                if pet:
                    pet_id_str = str(pet.get("_id", "None"))
                    print(f"[DEBUG] Pet {idx}: _id={pet_id_str}, name={pet.get('name', 'None')}, userId={pet.get('userId', 'None')}")
            
            # First, try with the _id field and ObjectId
            try:
                print(f"[DEBUG] Attempting to lookup with ObjectId...")
                obj_id = ObjectId(pet_id)
                print(f"[DEBUG] Created ObjectId: {obj_id}")
                pet = await async_pets_collection.find_one({"_id": obj_id})
                if pet:
                    print(f"[DEBUG] Found pet with _id as ObjectId: {pet_id}")
                    pet["_id"] = str(pet["_id"])
                    return Pet(**pet) if pet else None
                else:
                    print(f"[DEBUG] No pet found with ObjectId: {obj_id}")
            except Exception as e:
                print(f"[DEBUG] Error looking up by ObjectId: {str(e)}")
            
            # Next, try with string _id
            print(f"[DEBUG] Attempting to lookup with string _id...")
            pet = await async_pets_collection.find_one({"_id": pet_id})
            if pet:
                print(f"[DEBUG] Found pet with _id as string: {pet_id}")
                pet["_id"] = str(pet["_id"])
                return Pet(**pet) if pet else None
            else:
                print(f"[DEBUG] No pet found with string _id: {pet_id}")
            
            # Next, try with the id field (frontend might be passing this)
            print(f"[DEBUG] Attempting to lookup with id field...")
            pet = await async_pets_collection.find_one({"id": pet_id})
            if pet:
                print(f"[DEBUG] Found pet with id field: {pet_id}")
                pet["_id"] = str(pet["_id"])
                return Pet(**pet) if pet else None
            else:
                print(f"[DEBUG] No pet found with id field: {pet_id}")
                
            print(f"[DEBUG] No pet found with any ID format for {pet_id}")
            return None
        except Exception as e:
            print(f"[DEBUG] Unexpected error in get_pet: {str(e)}")
            return None

    @staticmethod
    async def get_pets_by_user(user_id: str) -> List[Pet]:
        """Get all pets for a user"""
        try:
            cursor = async_pets_collection.find({"userId": user_id})
            pets = []
            async for pet in cursor:
                if pet:
                    pet["_id"] = str(pet["_id"])
                    pets.append(Pet(**pet))
            return pets
        except Exception as e:
            print(f"Error getting pets for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def update_pet(pet_id: str, pet_data: dict) -> Optional[Pet]:
        try:
            # Remove None values from update data
            update_data = {k: v for k, v in pet_data.items() if v is not None}
            
            if not update_data:
                return await PetDB.get_pet(pet_id)
            
            # Try to handle the pet_id as ObjectId or string
            try:
                if ObjectId.is_valid(pet_id):
                    # Valid ObjectId format
                    result = await async_pets_collection.update_one(
                        {"_id": ObjectId(pet_id)},
                        {"$set": update_data}
                    )
                else:
                    # Try string IDs
                    result = await async_pets_collection.update_one(
                        {"$or": [{"_id": pet_id}, {"id": pet_id}]},
                        {"$set": update_data}
                    )
                
                if result.matched_count == 0:
                    print(f"[DEBUG] No pet matched for update with ID: {pet_id}")
                    return None
                    
            except Exception as e:
                print(f"[DEBUG] Error updating pet {pet_id}: {str(e)}")
                return None
            
            # Get the updated pet
            return await PetDB.get_pet(pet_id)
        except Exception as e:
            print(f"[DEBUG] Unexpected error in update_pet: {str(e)}")
            return None

    @staticmethod
    async def delete_pet(pet_id: str) -> bool:
        try:
            if ObjectId.is_valid(pet_id):
                result = await async_pets_collection.delete_one({"_id": ObjectId(pet_id)})
            else:
                result = await async_pets_collection.delete_one({"$or": [{"_id": pet_id}, {"id": pet_id}]})
            return result.deleted_count > 0
        except Exception as e:
            print(f"[DEBUG] Error deleting pet {pet_id}: {str(e)}")
            return False

    @staticmethod
    async def add_memory(pet_id: str, memory: str) -> Optional[Pet]:
        try:
            # Try to handle the pet_id as ObjectId or string
            try:
                if ObjectId.is_valid(pet_id):
                    # Valid ObjectId format
                    result = await async_pets_collection.update_one(
                        {"_id": ObjectId(pet_id)},
                        {"$push": {"memoryLog": memory}}
                    )
                else:
                    # Try string IDs
                    result = await async_pets_collection.update_one(
                        {"$or": [{"_id": pet_id}, {"id": pet_id}]},
                        {"$push": {"memoryLog": memory}}
                    )
                
                if result.matched_count == 0:
                    print(f"[DEBUG] No pet matched for memory update with ID: {pet_id}")
                    return None
                    
            except Exception as e:
                print(f"[DEBUG] Error adding memory to pet {pet_id}: {str(e)}")
                return None
                
            # Get the updated pet
            return await PetDB.get_pet(pet_id)
        except Exception as e:
            print(f"[DEBUG] Unexpected error in add_memory: {str(e)}")
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
            new_sass_level = min(pet.sassLevel + sass_increase, SASS_LEVELS["SAVAGE"])
            
            # Update pet state based on neglect
            updates = {
                "mood": MOOD_LEVELS["GRUMPY"],
                "sassLevel": new_sass_level,
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
        new_sass_level = pet.sassLevel
        
        # Update sass level based on interaction milestones
        if new_interaction_count >= 100 and pet.sassLevel < SASS_LEVELS["SAVAGE"]:
            new_sass_level = SASS_LEVELS["SAVAGE"]
        elif new_interaction_count >= 50 and pet.sassLevel < SASS_LEVELS["SASSY"]:
            new_sass_level = SASS_LEVELS["SASSY"]
        elif new_interaction_count >= 25 and pet.sassLevel < SASS_LEVELS["SNARKY"]:
            new_sass_level = SASS_LEVELS["SNARKY"]
        elif new_interaction_count >= 10 and pet.sassLevel < SASS_LEVELS["PLAYFUL"]:
            new_sass_level = SASS_LEVELS["PLAYFUL"]
            
        return await PetDB.update_pet(pet_id, {
            "interactionCount": new_interaction_count,
            "sassLevel": new_sass_level,
            "lastInteraction": datetime.now(timezone.utc)
        })

    @staticmethod
    async def get_sass_level(pet_id: str) -> Optional[int]:
        """Get the current sass level of a pet"""
        pet = await PetDB.get_pet(pet_id)
        return pet.sassLevel if pet else None
    
    # New comprehensive interaction methods
    @staticmethod
    async def feed_pet(pet_id: str) -> Optional[Pet]:
        """Comprehensive method to handle feeding a pet"""
        try:
            print(f"[DB] Processing feed action for pet: {pet_id}")
            
            # Update pet's feeding timestamp and mood
            await PetDB.update_last_fed(pet_id)
            await PetDB.update_mood(pet_id, "happy")
            
            # Record the interaction in memory log
            await PetDB.add_memory(pet_id, "Pet was fed and enjoyed the meal!")
            
            # Increment interaction count and update last interaction time
            return await PetDB.increment_interaction(pet_id)
        except Exception as e:
            print(f"[DB] Error in feed_pet: {str(e)}")
            return None
            
    @staticmethod
    async def play_with_pet(pet_id: str) -> Optional[Pet]:
        """Comprehensive method to handle playing with a pet"""
        try:
            print(f"[DB] Processing play action for pet: {pet_id}")
            
            # Update pet's mood to excited
            await PetDB.update_mood(pet_id, "excited")
            
            # Record the interaction in memory log
            await PetDB.add_memory(pet_id, "Pet played and had a great time!")
            
            # Increment interaction count and update last interaction time
            return await PetDB.increment_interaction(pet_id)
        except Exception as e:
            print(f"[DB] Error in play_with_pet: {str(e)}")
            return None
            
    @staticmethod
    async def teach_pet(pet_id: str, lesson: str) -> Optional[Pet]:
        """Comprehensive method to handle teaching a pet something new"""
        try:
            print(f"[DB] Processing teach action for pet: {pet_id}, lesson: {lesson}")
            
            # Get current pet to update level
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                print(f"[DB] Pet not found with ID: {pet_id}")
                return None
                
            # Add the lesson to pet's memory
            await PetDB.add_memory(pet_id, f"Learned: {lesson}")
            
            # Increase pet's level
            await PetDB.update_level(pet_id, pet.level + 1)
            
            # Increment interaction count and update last interaction time
            return await PetDB.increment_interaction(pet_id)
        except Exception as e:
            print(f"[DB] Error in teach_pet: {str(e)}")
            return None 