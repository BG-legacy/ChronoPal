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

print(f"Connecting to MongoDB database: {DB_NAME}")
# Don't print full URI as it contains credentials
uri_parts = MONGODB_URI.split('@') if MONGODB_URI else []
if len(uri_parts) > 1:
    safe_uri = f"...@{uri_parts[-1]}"
    print(f"Using MongoDB URI: {safe_uri}")

if not MONGODB_URI or not DB_NAME:
    raise ValueError("MongoDB connection settings are not properly configured in environment variables")

# Initialize MongoDB client with updated SSL settings
try:
    import ssl
    import certifi
    
    print("Connecting to MongoDB...")
    
    # Connect using minimal parameters and rely on URI parameters
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000
    )

    # Test the connection - only log errors, don't fail
    try:
        server_info = client.server_info()
        print(f"Successfully connected to MongoDB version: {server_info.get('version', 'unknown')}")
        print(f"Available databases: {client.list_database_names()}")
    except Exception as e:
        print(f"Warning: MongoDB connection test failed: {str(e)}")
        print(f"MongoDB URI format (redacted): {safe_uri}")
        # Don't raise the error - we'll attempt to continue anyway
        
    db = client[DB_NAME]
    pets_collection = db["pets"]
    users_collection = db["users"]
    
    # Print existing collections
    print(f"Collections in {DB_NAME}: {db.list_collection_names()}")

    # Async client for FastAPI with minimal parameters
    print("Setting up async MongoDB client...")
    async_client = AsyncIOMotorClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000
    )

    async_db = async_client[DB_NAME]
    async_pets_collection = async_db["pets"]
    async_users_collection = async_db["users"]
    print("Async MongoDB client setup complete")
except Exception as e:
    print(f"Error setting up MongoDB connection: {str(e)}")
    # Create empty placeholder collections for testing/development
    # This allows the app to start even if MongoDB is not available
    class MockCollection:
        async def find_one(self, *args, **kwargs):
            print("Warning: Using mock database connection")
            return None
        
        async def find(self, *args, **kwargs):
            print("Warning: Using mock database connection")
            class MockCursor:
                def __aiter__(self):
                    return self
                async def __anext__(self):
                    raise StopAsyncIteration
                def limit(self, *args, **kwargs):
                    return self
            return MockCursor()
        
        async def insert_one(self, *args, **kwargs):
            print("Warning: Using mock database connection")
            class MockResult:
                @property
                def inserted_id(self):
                    return "mock_id"
            return MockResult()
        
        async def update_one(self, *args, **kwargs):
            print("Warning: Using mock database connection")
            return None
        
        async def delete_one(self, *args, **kwargs):
            print("Warning: Using mock database connection")
            class MockResult:
                @property
                def deleted_count(self):
                    return 0
            return MockResult()
    
    async_pets_collection = MockCollection()
    async_users_collection = MockCollection()

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