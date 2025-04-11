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
from pymongo.server_api import ServerApi
import certifi

# Load environment variables
load_dotenv()

# MongoDB connection string and database name
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

print(f"Connecting to MongoDB database: {DB_NAME}")
# Don't print full URI as it contains credentials
uri_parts = MONGODB_URI.split('@') if MONGODB_URI else []
if len(uri_parts) > 1:
    safe_uri = f"...@{uri_parts[-1]}"
    print(f"Using MongoDB URI: {safe_uri}")

if not MONGODB_URI or not DB_NAME:
    raise ValueError("MongoDB connection settings are not properly configured in environment variables")

# Function to get the MongoDB client - will be overridden by the function from routes
async def get_client():
    try:
        client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=10,
            minPoolSize=0,
            maxIdleTimeMS=50000,
            tlsCAFile=certifi.where()
        )
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        raise

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserDB:
    @staticmethod
    async def create_user(user: UserCreate) -> User:
        # Import here to avoid circular import
        from api.routes import get_mongo_client_func
        client = get_mongo_client_func()
        db = client[DB_NAME]
        users_collection = db["users"]
        
        hashed_password = UserDB.get_password_hash(user.password)
        user_dict = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc)
        }
        result = await users_collection.insert_one(user_dict)
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        if created_user:
            created_user["_id"] = str(created_user["_id"])
        return User(**created_user)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        # Import here to avoid circular import
        from api.routes import get_mongo_client_func
        client = get_mongo_client_func()
        db = client[DB_NAME]
        users_collection = db["users"]
        
        user = await users_collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return User(**user) if user else None

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        try:
            # Import here to avoid circular import
            from api.routes import get_mongo_client_func
            client = get_mongo_client_func()
            db = client[DB_NAME]
            users_collection = db["users"]
            
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return User(**user) if user else None
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
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
            # Import here to avoid circular import
            from api.routes import get_mongo_client_func
            client = get_mongo_client_func()
            db = client[DB_NAME]
            users_collection = db["users"]
            
            result = await users_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False

class PetDB:
    @staticmethod
    async def create_pet(pet_data: Union[Pet, Dict]) -> Pet:
        # Import here to avoid circular import
        from api.routes import get_mongo_client_func
        client = get_mongo_client_func()
        db = client[DB_NAME]
        pets_collection = db["pets"]
        
        # Convert to dict if it's a Pydantic model
        if isinstance(pet_data, Pet):
            pet_data = pet_data.model_dump()
        
        # Ensure required fields
        if "created_at" not in pet_data:
            pet_data["created_at"] = datetime.now(timezone.utc)
        if "last_fed" not in pet_data:
            pet_data["last_fed"] = datetime.now(timezone.utc)
        if "last_interaction" not in pet_data:
            pet_data["last_interaction"] = datetime.now(timezone.utc)
        if "memories" not in pet_data:
            pet_data["memories"] = []
        if "mood" not in pet_data:
            pet_data["mood"] = "happy"
        if "level" not in pet_data:
            pet_data["level"] = 1
        if "evolve_stage" not in pet_data:
            pet_data["evolve_stage"] = "baby"
        if "battery_level" not in pet_data:
            pet_data["battery_level"] = 100
        if "interactions_today" not in pet_data:
            pet_data["interactions_today"] = 0
        if "last_interaction_reset" not in pet_data:
            pet_data["last_interaction_reset"] = datetime.now(timezone.utc)
        
        result = await pets_collection.insert_one(pet_data)
        created_pet = await pets_collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string for return value
        if created_pet:
            created_pet["_id"] = str(created_pet["_id"])
        
        return Pet(**created_pet)

    @staticmethod
    async def get_pet(pet_id: str) -> Optional[Pet]:
        try:
            # Import here to avoid circular import
            from api.routes import get_mongo_client_func
            client = get_mongo_client_func()
            db = client[DB_NAME]
            pets_collection = db["pets"]
            
            pet = await pets_collection.find_one({"_id": ObjectId(pet_id)})
            if not pet:
                return None
                
            # Convert datetime strings to datetime objects if needed
            for date_field in ["created_at", "last_fed", "last_interaction", "last_interaction_reset"]:
                if date_field in pet and isinstance(pet[date_field], str):
                    try:
                        pet[date_field] = datetime.fromisoformat(pet[date_field].replace("Z", "+00:00"))
                    except ValueError:
                        # If we can't parse it, leave it as is
                        pass
            
            # Convert BSON ObjectId to string
            pet["_id"] = str(pet["_id"])
            
            # Check for neglect state
            pet_obj = Pet(**pet)
            
            # Calculate time since last interaction
            now = datetime.now(timezone.utc)
            last_interaction = pet.get("last_interaction", now - timedelta(days=1))
            if isinstance(last_interaction, str):
                try:
                    last_interaction = datetime.fromisoformat(last_interaction.replace("Z", "+00:00"))
                except ValueError:
                    last_interaction = now - timedelta(days=1)
            
            hours_since_interaction = (now - last_interaction).total_seconds() / 3600
            
            # Update mood based on neglect if needed
            if hours_since_interaction >= NEGLECT_THRESHOLD_HOURS:
                level = int(hours_since_interaction / NEGLECT_THRESHOLD_HOURS)
                idx = min(level, len(MOOD_LEVELS) - 1)  # Ensure we don't go out of bounds
                pet_obj.mood = MOOD_LEVELS[idx]
                
                # Save the updated mood
                await PetDB.update_pet(pet_id, {"mood": pet_obj.mood})
            
            # Check if we need to reset daily interaction counter
            last_reset = pet.get("last_interaction_reset", now - timedelta(days=1))
            if isinstance(last_reset, str):
                try:
                    last_reset = datetime.fromisoformat(last_reset.replace("Z", "+00:00"))
                except ValueError:
                    last_reset = now - timedelta(days=1)
            
            if last_reset.date() < now.date():
                # It's a new day, reset the counter
                pet_obj.interactions_today = 0
                pet_obj.last_interaction_reset = now
                await PetDB.update_pet(pet_id, {
                    "interactions_today": 0,
                    "last_interaction_reset": now
                })
            
            return pet_obj
        except Exception as e:
            print(f"Error getting pet: {str(e)}")
            return None

    @staticmethod
    async def get_pets_by_user(user_id: str) -> List[Pet]:
        try:
            # Import here to avoid circular import
            from api.routes import get_mongo_client_func
            client = get_mongo_client_func()
            db = client[DB_NAME]
            pets_collection = db["pets"]
            
            cursor = pets_collection.find({"user_id": user_id})
            pets = []
            async for doc in cursor:
                # Convert ObjectId to string for each pet
                doc["_id"] = str(doc["_id"])
                pets.append(Pet(**doc))
            return pets
        except Exception as e:
            print(f"Error getting pets by user: {str(e)}")
            return []

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
        """Check if the pet is being neglected and update its mood accordingly"""
        try:
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None
                
            now = datetime.now(timezone.utc)
            
            # Calculate how long since the pet was last fed or interacted with
            last_fed = pet.lastFed
            last_interaction = pet.lastInteraction
            
            # Convert to UTC if they're not already
            if last_fed.tzinfo is None:
                last_fed = last_fed.replace(tzinfo=timezone.utc)
            if last_interaction.tzinfo is None:
                last_interaction = last_interaction.replace(tzinfo=timezone.utc)
            
            # Calculate hours since last interaction
            hours_since_fed = (now - last_fed).total_seconds() / 3600
            hours_since_interaction = (now - last_interaction).total_seconds() / 3600
            
            # Determine which was more recent, feeding or other interaction
            hours_since_last_action = min(hours_since_fed, hours_since_interaction)
            
            # Determine new mood based on neglect time
            new_mood = pet.mood  # Default to current mood
            
            if hours_since_last_action < NEGLECT_THRESHOLD_HOURS / 4:  # Less than 6 hours
                new_mood = MOOD_LEVELS["HAPPY"]
            elif hours_since_last_action < NEGLECT_THRESHOLD_HOURS / 2:  # Less than 12 hours
                new_mood = MOOD_LEVELS["CONTENT"]
            elif hours_since_last_action < NEGLECT_THRESHOLD_HOURS * 0.75:  # Less than 18 hours
                new_mood = MOOD_LEVELS["NEUTRAL"]
            elif hours_since_last_action < NEGLECT_THRESHOLD_HOURS:  # Less than 24 hours
                new_mood = MOOD_LEVELS["GRUMPY"]
            else:  # 24 hours or more
                new_mood = MOOD_LEVELS["ANGRY"]
            
            # Calculate battery depletion based on neglect time
            # Deplete battery by 1% per hour of neglect
            hours_of_neglect = hours_since_last_action
            battery_depletion = int(hours_of_neglect)
            
            # Ensure batteryLevel exists and is a number
            current_battery = getattr(pet, 'batteryLevel', 100)
            if current_battery is None:
                current_battery = 100
                
            # Calculate new battery level (minimum 0)
            new_battery_level = max(0, current_battery - battery_depletion)
            
            # Only update if there's a change in mood or battery
            if new_mood != pet.mood or new_battery_level != current_battery:
                update_data = {
                    "mood": new_mood,
                    "batteryLevel": new_battery_level
                }
                updated_pet = await PetDB.update_pet(pet_id, update_data)
                return updated_pet
            
            return pet
        except Exception as e:
            print(f"Error checking neglect: {str(e)}")
            return None
            
    @staticmethod
    async def update_battery_level(pet_id: str, amount: int) -> Optional[Pet]:
        """Update the pet's battery level, ensuring it stays between 0 and 100"""
        try:
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None
                
            # Get current battery level, defaulting to 100 if not set
            current_battery = getattr(pet, 'batteryLevel', 100)
            if current_battery is None:
                current_battery = 100
                
            # Calculate new battery level with bounds
            new_battery_level = max(0, min(100, current_battery + amount))
            
            # Only update if there's a change
            if new_battery_level != current_battery:
                updated_pet = await PetDB.update_pet(pet_id, {"batteryLevel": new_battery_level})
                return updated_pet
            
            return pet
        except Exception as e:
            print(f"Error updating battery level: {str(e)}")
            return None
            
    @staticmethod
    async def is_battery_depleted(pet_id: str) -> bool:
        """Check if the pet's battery is depleted (0 or below)"""
        try:
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return False
                
            # Get battery level, defaulting to 100 if not set
            battery_level = getattr(pet, 'batteryLevel', 100)
            if battery_level is None:
                battery_level = 100
                
            return battery_level <= 0
        except Exception as e:
            print(f"Error checking battery depletion: {str(e)}")
            return False

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
        """Feed the pet, updating its mood and last feed time"""
        try:
            # Get the pet
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None
            
            # Check if the pet's battery is depleted - can't feed a "dead" pet
            battery_level = getattr(pet, 'batteryLevel', 100) 
            if battery_level is not None and battery_level <= 0:
                return pet  # Can't feed a "dead" pet
                
            now = datetime.now(timezone.utc)
            
            # Update the pet
            updates = {
                "lastFed": now,
                "lastInteraction": now,
                "mood": MOOD_LEVELS["HAPPY"]  # Feeding always makes pet happy
            }
            
            # Increase battery by 10%
            await PetDB.update_battery_level(pet_id, 10)
            
            # Increment interaction count
            await PetDB.increment_interaction(pet_id)
            
            # Add the memory
            await PetDB.add_memory(pet_id, "I was fed and it was delicious!")
            
            # Update the pet and get the updated version
            return await PetDB.update_pet(pet_id, updates)
        except Exception as e:
            print(f"Error feeding pet: {str(e)}")
            return None

    @staticmethod
    async def play_with_pet(pet_id: str) -> Optional[Pet]:
        """Play with the pet, updating its mood and last interaction time"""
        try:
            # Get the pet
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None
                
            # Check if the pet's battery is depleted - can't play with a "dead" pet
            battery_level = getattr(pet, 'batteryLevel', 100) 
            if battery_level is not None and battery_level <= 0:
                return pet  # Can't play with a "dead" pet
            
            now = datetime.now(timezone.utc)
            
            # Update the pet
            updates = {
                "lastInteraction": now,
                "mood": MOOD_LEVELS["HAPPY"]  # Playing always makes pet happy
            }
            
            # Increase battery by 5%
            await PetDB.update_battery_level(pet_id, 5)
            
            # Increment interaction count
            await PetDB.increment_interaction(pet_id)
            
            # Add the memory
            await PetDB.add_memory(pet_id, "We played together and it was fun!")
            
            # Update the pet and get the updated version
            return await PetDB.update_pet(pet_id, updates)
        except Exception as e:
            print(f"Error playing with pet: {str(e)}")
            return None

    @staticmethod
    async def teach_pet(pet_id: str, lesson: str) -> Optional[Pet]:
        """Teach the pet something, updating its level and last interaction time"""
        try:
            # Get the pet
            pet = await PetDB.get_pet(pet_id)
            if not pet:
                return None
                
            # Check if the pet's battery is depleted - can't teach a "dead" pet
            battery_level = getattr(pet, 'batteryLevel', 100) 
            if battery_level is not None and battery_level <= 0:
                return pet  # Can't teach a "dead" pet
            
            now = datetime.now(timezone.utc)
            
            # Update the pet
            updates = {
                "lastInteraction": now,
                "level": pet.level + 1  # Teaching increases pet's level
            }
            
            # Increase battery by 7%
            await PetDB.update_battery_level(pet_id, 7)
            
            # Increment interaction count
            await PetDB.increment_interaction(pet_id)
            
            # Add the memory of what was taught
            await PetDB.add_memory(pet_id, f"I learned about {lesson}")
            
            # Update the pet and get the updated version
            return await PetDB.update_pet(pet_id, updates)
        except Exception as e:
            print(f"Error teaching pet: {str(e)}")
            return None 