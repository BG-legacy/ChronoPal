from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from typing import Optional, Dict, Any, List, Callable
from pydantic import BaseModel
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from database.pet_schema import Pet
from database.user_schema import User, UserCreate, UserLogin
from database.database import PetDB, UserDB
from .ai_personality import get_chronopal_response
from bson import ObjectId
import certifi

# Load environment variables
load_dotenv()

router = APIRouter()

# Store active sessions (in production, use a proper session store)
active_sessions = {}
get_mongo_client_func = None

# Store session management functions
session_functions = None

def set_active_sessions(sessions_dict):
    """Set the active sessions dictionary from the main app"""
    global active_sessions
    active_sessions = sessions_dict
    print(f"Session store initialized with {len(active_sessions)} existing sessions")

def set_mongo_client(client_func: Callable):
    """Set the MongoDB client function from main app.
    
    This function sets the global get_mongo_client_func that is used by the database
    operations to get a MongoDB client instance.
    
    Args:
        client_func: A callable that returns a MongoDB client instance
    """
    global get_mongo_client_func
    get_mongo_client_func = client_func
    print("MongoDB client function initialized")

def set_session_functions(functions_dict: dict):
    """Set the session management functions from the main app"""
    global session_functions
    session_functions = functions_dict
    print("Session management functions initialized")

# Simple health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "ChronoPal API",
        "version": "1.0.0",
        "active_sessions": len(active_sessions)
    }

class InteractionRequest(BaseModel):
    pet_id: str
    interaction_type: str  # "feed", "play", or "teach"
    message: Optional[str] = None
    
    def validate_interaction_type(self):
        valid_types = ["feed", "play", "teach"]
        if self.interaction_type not in valid_types:
            raise ValueError(f"interaction_type must be one of: {', '.join(valid_types)}")
        
        # For "teach" interactions, a message is required
        if self.interaction_type == "teach" and not self.message:
            raise ValueError("Message is required for 'teach' interactions")
        
        return True

class ChatRequest(BaseModel):
    message: str
    pet_id: str

class FeedPetRequest(BaseModel):
    pet_id: str

class PlayPetRequest(BaseModel):
    pet_id: str

class TeachPetRequest(BaseModel):
    pet_id: str
    message: str

async def get_current_user(session_id: str = Header(None, alias="session-id")):
    if not session_id:
        print(f"[AUTH ERROR] No session ID provided in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    print(f"[AUTH DEBUG] Session ID received: {session_id[:8]}...")
    
    if not session_functions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session management not initialized"
        )
    
    session = await session_functions["get_session"](session_id)
    if not session:
        print(f"[AUTH ERROR] Session not found or expired: {session_id[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    print(f"[AUTH DEBUG] Found user_id: {session['user_id']} for session: {session_id[:8]}...")
    
    user = await UserDB.get_user_by_id(session['user_id'])
    if not user:
        print(f"[AUTH ERROR] User not found for ID: {session['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    print(f"[AUTH DEBUG] Successfully authenticated user: {user.username}")
    return user

# Authentication routes
@router.post("/register", response_model=User)
async def register(user: UserCreate):
    try:
        print(f"Received registration request: {user.model_dump()}")
        
        # Validate input
        if not user.email or not user.password or not user.username:
            print(f"Missing required fields: email={user.email}, password={user.password}, username={user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email, password, and username are required"
            )
        
        # Check if user already exists
        existing_user = await UserDB.get_user_by_email(user.email)
        if existing_user:
            print(f"User already exists with email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        try:
            print("Attempting to create user...")
            created_user = await UserDB.create_user(user)
            print(f"Successfully created user: {created_user.model_dump()}")
            
            # Create session if session management is available
            if session_functions and session_functions.get("create_session"):
                try:
                    session_id = await session_functions["create_session"](str(created_user.id))
                    print(f"Created session for new user: {session_id[:8]}...")
                except Exception as session_error:
                    print(f"Warning: Failed to create session for new user: {str(session_error)}")
                    # Don't fail registration if session creation fails
            
            return created_user
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/login")
async def login(user_login: UserLogin):
    print(f"[LOGIN] Login attempt for email: {user_login.email}")
    
    user = await UserDB.get_user_by_email(user_login.email)
    if not user:
        print(f"[LOGIN ERROR] User not found with email: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    if not UserDB.verify_password(user_login.password, user.hashed_password):
        print(f"[LOGIN ERROR] Invalid password for user: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not session_functions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session management not initialized"
        )
    
    # Create a session in MongoDB
    session_id = await session_functions["create_session"](str(user.id))
    
    print(f"[LOGIN SUCCESS] Created session {session_id[:8]}... for user {user.username} (ID: {user.id})")
    
    return {"session_id": session_id, "user": user}

@router.post("/logout")
async def logout(session_id: str = Header(None, alias="session-id")):
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if not session_functions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session management not initialized"
        )
    
    await session_functions["delete_session"](session_id)
    return {"message": "Logged out successfully"}

# Protected routes
@router.get("/user-pet", response_model=Pet)
async def get_user_pet(current_user: User = Depends(get_current_user)):
    """Get the current user's pet"""
    try:
        # Get all pets for the user
        pets = await PetDB.get_pets_by_user(current_user.id)
        if not pets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pets found for user"
            )
        # Return the first pet (users currently only have one pet)
        pet = pets[0]
        
        # Ensure the pet has both id and _id for frontend compatibility
        pet_dict = pet.model_dump()
        if '_id' in pet_dict and not pet_dict.get('id'):
            pet_dict['id'] = pet_dict['_id']
        
        print(f"Returning pet with ID: {pet_dict.get('id') or pet_dict.get('_id')}")
        return pet_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user pet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user pet: {str(e)}"
        )

@router.post("/feed-pet")
async def feed_pet(request: FeedPetRequest, current_user: User = Depends(get_current_user)):
    """Feed the pet"""
    try:
        pet_id = request.pet_id
        print(f"Received feed request for pet: {pet_id}")
        
        pet = await PetDB.get_pet(pet_id)
        if not pet:
            print(f"Pet not found with ID: {pet_id}")
            raise HTTPException(status_code=404, detail="Pet not found")
        
        if pet.userId != str(current_user.id):
            print(f"Authentication error: User {current_user.id} tried to access pet {pet.id} belonging to {pet.userId}")
            raise HTTPException(status_code=403, detail="Not authorized to interact with this pet")

        # Use the comprehensive feed_pet method instead of individual operations
        updated_pet = await PetDB.feed_pet(pet_id)
        
        if not updated_pet:
            print(f"Pet not found after update: {pet_id}")
            raise HTTPException(status_code=404, detail="Pet not found after update")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"Feed interaction successful. Updated pet ID: {updated_pet_dict.get('id') or updated_pet_dict.get('_id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"Error in feed_pet: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/feed-pet-by-user")
async def feed_pet_by_user(current_user: User = Depends(get_current_user)):
    """Feed the pet without requiring pet_id - automatically fetches user's pet"""
    try:
        print(f"[API] Feed pet by user request for user ID: {current_user.id}")
        
        # Get the user's pet
        pets = await PetDB.get_pets_by_user(current_user.id)
        if not pets:
            print(f"[API] No pets found for user: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pets found for user"
            )
        
        # Use the first pet (users currently only have one pet)
        pet = pets[0]
        
        # Check if pet's battery is depleted
        if getattr(pet, 'batteryLevel', 100) <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pet's battery is depleted. Reset your pet to continue."
            )
        
        # Feed the pet
        updated_pet = await PetDB.feed_pet(str(pet.id))
        
        if not updated_pet:
            print(f"[API] Pet not found after update: {pet.id}")
            raise HTTPException(status_code=404, detail="Pet not found after update")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"[API] Feed interaction successful. Updated pet ID: {updated_pet_dict.get('id') or updated_pet_dict.get('_id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"[API] Error in feed_pet_by_user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to feed pet: {str(e)}"
        )

@router.post("/play-with-pet")
async def play_with_pet(request: PlayPetRequest, current_user: User = Depends(get_current_user)):
    """Play with the pet"""
    try:
        pet_id = request.pet_id
        print(f"Received play request for pet: {pet_id}")
        
        pet = await PetDB.get_pet(pet_id)
        if not pet:
            print(f"Pet not found with ID: {pet_id}")
            raise HTTPException(status_code=404, detail="Pet not found")
        
        if pet.userId != str(current_user.id):
            print(f"Authentication error: User {current_user.id} tried to access pet {pet.id} belonging to {pet.userId}")
            raise HTTPException(status_code=403, detail="Not authorized to interact with this pet")

        # Use the comprehensive play_with_pet method instead of individual operations
        updated_pet = await PetDB.play_with_pet(pet_id)
        
        if not updated_pet:
            print(f"Pet not found after update: {pet_id}")
            raise HTTPException(status_code=404, detail="Pet not found after update")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"Play interaction successful. Updated pet ID: {updated_pet_dict.get('id') or updated_pet_dict.get('_id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"Error in play_with_pet: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/play-with-pet-by-user")
async def play_with_pet_by_user(current_user: User = Depends(get_current_user)):
    """Play with the pet without requiring pet_id - automatically fetches user's pet"""
    try:
        print(f"[API] Play with pet by user request for user ID: {current_user.id}")
        
        # Get the user's pet
        pets = await PetDB.get_pets_by_user(current_user.id)
        if not pets:
            print(f"[API] No pets found for user: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pets found for user"
            )
        
        # Use the first pet (users currently only have one pet)
        pet = pets[0]
        
        # Check if pet's battery is depleted
        if getattr(pet, 'batteryLevel', 100) <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pet's battery is depleted. Reset your pet to continue."
            )
        
        # Play with the pet
        updated_pet = await PetDB.play_with_pet(str(pet.id))
        
        if not updated_pet:
            print(f"[API] Pet not found after update: {pet.id}")
            raise HTTPException(status_code=404, detail="Pet not found after update")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"[API] Play interaction successful. Updated pet ID: {updated_pet_dict.get('id') or updated_pet_dict.get('_id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"[API] Error in play_with_pet_by_user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to play with pet: {str(e)}"
        )

@router.post("/teach-pet")
async def teach_pet(request: TeachPetRequest, current_user: User = Depends(get_current_user)):
    """Teach the pet something new"""
    try:
        pet_id = request.pet_id
        message = request.message
        print(f"Received teach request for pet: {pet_id}, message: {message}")
        
        if not message or message.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message is required for 'teach' interactions"
            )
        
        pet = await PetDB.get_pet(pet_id)
        if not pet:
            print(f"Pet not found with ID: {pet_id}")
            raise HTTPException(status_code=404, detail="Pet not found")
        
        if pet.userId != str(current_user.id):
            print(f"Authentication error: User {current_user.id} tried to access pet {pet.id} belonging to {pet.userId}")
            raise HTTPException(status_code=403, detail="Not authorized to interact with this pet")

        # Use the comprehensive teach_pet method instead of individual operations
        updated_pet = await PetDB.teach_pet(pet_id, message)
        
        if not updated_pet:
            print(f"Pet not found after update: {pet_id}")
            raise HTTPException(status_code=404, detail="Pet not found after update")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"Teach interaction successful. Updated pet ID: {updated_pet_dict.get('id') or updated_pet_dict.get('_id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"Error in teach_pet: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

class TeachPetByUserRequest(BaseModel):
    message: str

@router.post("/teach-pet-by-user")
async def teach_pet_by_user(request: TeachPetByUserRequest, current_user: User = Depends(get_current_user)):
    """Teach the pet without requiring pet_id - automatically fetches user's pet"""
    try:
        print(f"[API] Teach pet by user request for user ID: {current_user.id}, message: {request.message}")
        
        # Get the user's pet
        pets = await PetDB.get_pets_by_user(current_user.id)
        if not pets:
            print(f"[API] No pets found for user: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pets found for user"
            )
        
        # Use the first pet (users currently only have one pet)
        pet = pets[0]
        
        # Check if pet's battery is depleted
        if getattr(pet, 'batteryLevel', 100) <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pet's battery is depleted. Reset your pet to continue."
            )
        
        # Validate the message
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message is required for teaching"
            )
            
        # Teach the pet
        updated_pet = await PetDB.teach_pet(str(pet.id), request.message)
        
        if not updated_pet:
            print(f"[API] Pet not found after update: {pet.id}")
            raise HTTPException(status_code=404, detail="Pet not found after update")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"[API] Teach interaction successful. Updated pet ID: {updated_pet_dict.get('id') or updated_pet_dict.get('_id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"[API] Error in teach_pet_by_user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to teach pet: {str(e)}"
        )

@router.post("/save-pet", response_model=Pet)
async def save_pet(pet_data: dict, current_user: User = Depends(get_current_user)):
    """Save pet data to database"""
    try:
        # Add the current user ID to the pet data
        pet_data["userId"] = str(current_user.id)
        
        # Create the pet in the database
        saved_pet = await PetDB.create_pet(pet_data)
        if not saved_pet:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save pet"
            )
        return saved_pet
    except Exception as e:
        print(f"Error in save_pet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save pet: {str(e)}"
        )

@router.post("/chat")
async def chat_with_pet(chat_request: ChatRequest, current_user: User = Depends(get_current_user)):
    """Chat with a pet and get a response based on its personality"""
    try:
        print(f"[API] Chat request for pet: {chat_request.pet_id}, message: {chat_request.message}")
        
        # If pet_id isn't provided correctly, try to get the user's pet
        if not chat_request.pet_id or chat_request.pet_id == 'null' or chat_request.pet_id == 'undefined':
            print(f"[API] No pet_id provided or invalid pet_id, getting user's pet")
            pets = await PetDB.get_pets_by_user(current_user.id)
            if pets:
                chat_request.pet_id = str(pets[0].id)
                print(f"[API] Using pet ID from user's pets: {chat_request.pet_id}")
            else:
                # If no pet found, create a new one
                print(f"[API] No pets found for user, creating a default pet")
                pet_data = {
                    "name": "Berny",
                    "species": "Digital",
                    "mood": "happy",
                    "level": 1,
                    "sassLevel": 1,
                    "batteryLevel": 100,
                    "userId": str(current_user.id),
                    "lastFed": datetime.now(timezone.utc),
                    "lastInteraction": datetime.now(timezone.utc),
                    "interactionCount": 0,
                    "memoryLog": []
                }
                new_pet = await PetDB.create_pet(pet_data)
                if new_pet:
                    chat_request.pet_id = str(new_pet.id)
                    print(f"[API] Created new pet with ID: {chat_request.pet_id}")
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create pet"
                    )
        
        # Get the pet - this might still fail if the ID exists but is invalid
        pet = await PetDB.get_pet(chat_request.pet_id)
        
        # If the pet is still not found, try one more strategy - get the first pet for this user
        if not pet:
            print(f"[API] Pet not found with ID: {chat_request.pet_id}, trying to find any pet for this user")
            pets = await PetDB.get_pets_by_user(current_user.id)
            if pets:
                pet = pets[0]
                chat_request.pet_id = str(pet.id)
                print(f"[API] Using alternative pet with ID: {chat_request.pet_id}")
            else:
                print(f"[API] No pets found for user {current_user.id}")
                raise HTTPException(status_code=404, detail="Pet not found")
        
        # Check if pet's battery is depleted
        if getattr(pet, 'batteryLevel', 100) <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pet's battery is depleted. Reset your pet to continue."
            )
        
        # Check if the user owns this pet
        if pet.userId != str(current_user.id):
            print(f"[API] Authentication error: User {current_user.id} tried to chat with pet {pet.id} belonging to {pet.userId}")
            
            # If user doesn't own this pet, try to get their actual pet
            print(f"[API] Attempting to find the correct pet for user {current_user.id}")
            pets = await PetDB.get_pets_by_user(current_user.id)
            if pets:
                pet = pets[0]
                chat_request.pet_id = str(pet.id)
                print(f"[API] Found correct pet with ID: {chat_request.pet_id}")
            else:
                raise HTTPException(status_code=403, detail="Not authorized to chat with this pet")
        
        # Remove any empty message
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message is required for chat"
            )
            
        # Calculate response and tone based on pet's attributes
        response = await get_chronopal_response(chat_request.message, pet)
        
        # Increment interaction count for the pet
        await PetDB.increment_interaction(chat_request.pet_id)
        
        # Deplete battery by 3% for chatting
        await PetDB.update_battery_level(chat_request.pet_id, -3)
        
        # Add the conversation to the pet's memory
        memory_entry = f"User said: '{chat_request.message}', I replied: '{response}'"
        await PetDB.add_memory(chat_request.pet_id, memory_entry)
        
        print(f"[API] Chat response generated successfully: {response[:50]}...")
        return {"response": response}
    except Exception as e:
        print(f"[API] Error in chat_with_pet: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to chat with pet: {str(e)}"
        )

@router.post("/debug-interaction")
async def debug_interaction(request_data: dict, current_user: User = Depends(get_current_user)):
    """Debug endpoint to test interaction request processing"""
    try:
        print(f"[DEBUG] Raw request data: {request_data}")
        
        # Check for required fields
        if "pet_id" not in request_data:
            return {"error": "Missing pet_id field", "received_data": request_data}
            
        if "interaction_type" not in request_data:
            return {"error": "Missing interaction_type field", "received_data": request_data}
            
        # Create an InteractionRequest object
        try:
            interaction = InteractionRequest(**request_data)
            print(f"[DEBUG] Successfully created InteractionRequest object: {interaction.model_dump()}")
            
            # Check if pet exists in database
            pet = await PetDB.get_pet(interaction.pet_id)
            if not pet:
                return {
                    "error": f"Pet not found with ID: {interaction.pet_id}",
                    "parsed_data": interaction.model_dump(),
                    "validation": "Request is valid but pet not found"
                }
                
            # Check if user owns this pet
            if pet.userId != str(current_user.id):
                return {
                    "error": f"User {current_user.id} not authorized to access pet {pet.id}",
                    "parsed_data": interaction.model_dump(),
                    "validation": "Request is valid but pet belongs to another user"
                }
                
            # All valid
            return {
                "success": True,
                "parsed_data": interaction.model_dump(),
                "pet_found": True,
                "pet_belongs_to_user": True,
                "pet_details": {
                    "id": pet.id,
                    "name": pet.name,
                    "level": pet.level,
                    "userId": pet.userId
                },
                "validation": "Request data is valid and pet exists"
            }
        except Exception as e:
            print(f"[DEBUG] Failed to create InteractionRequest: {str(e)}")
            return {
                "error": f"Failed to parse request: {str(e)}",
                "received_data": request_data
            }
            
    except Exception as e:
        print(f"[DEBUG] Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}", "received_data": request_data}

@router.get("/fixed-pet", response_model=Pet)
async def get_fixed_pet(current_user: User = Depends(get_current_user)):
    """Get a consistent pet for the user, creating one if none exists"""
    try:
        # First, always check the user's existing pets
        pets = await PetDB.get_pets_by_user(current_user.id)
        
        # Log debug info
        if pets:
            pet_ids = [p.id for p in pets]
            print(f"[FIXED_PET] Found {len(pets)} existing pets for user {current_user.id}: {pet_ids}")
        else:
            print(f"[FIXED_PET] No existing pets found for user {current_user.id}")
            
        if pets:
            # IMPORTANT: If user has pets, always return THE FIRST ONE for consistency
            # This is the key change to the endpoint to ensure it always returns the same pet
            pet = pets[0]
            pet_id = pet.id
            print(f"[FIXED_PET] Using existing pet with ID: {pet_id}")
            
            # Return the existing pet with both id and _id fields set
            pet_dict = pet.model_dump()
            if '_id' in pet_dict and not pet_dict.get('id'):
                pet_dict['id'] = pet_dict['_id']
            
            return pet_dict
        else:
            # If user has no pets, create one with standard defaults
            print(f"[FIXED_PET] Creating new pet for user {current_user.id}")
            pet_data = {
                "name": "Berny",
                "species": "Digital",
                "mood": "happy",
                "level": 1,
                "sassLevel": 1,
                "userId": str(current_user.id),
                "lastFed": datetime.now(timezone.utc),
                "lastInteraction": datetime.now(timezone.utc),
                "interactionCount": 0,
                "memoryLog": []
            }
            pet = await PetDB.create_pet(pet_data)
            print(f"[FIXED_PET] Created new pet with ID: {pet.id}")
            
            # Ensure the pet has both id and _id for frontend compatibility
            pet_dict = pet.model_dump()
            if '_id' in pet_dict and not pet_dict.get('id'):
                pet_dict['id'] = pet_dict['_id']
            
            return pet_dict
    except Exception as e:
        print(f"Error in get_fixed_pet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fixed pet: {str(e)}"
        )

@router.post("/reset-pet", response_model=Pet)
async def reset_pet(current_user: User = Depends(get_current_user)):
    """Reset a pet by creating a new one when battery is depleted"""
    try:
        print(f"[API] Reset pet request for user ID: {current_user.id}")
        
        # Get the user's pet
        pets = await PetDB.get_pets_by_user(current_user.id)
        
        # If the user has a pet, check if it's eligible for reset (battery depleted)
        if pets:
            pet = pets[0]
            battery_level = getattr(pet, 'batteryLevel', 0)
            
            # Only allow reset if battery is depleted or very low
            if battery_level > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pet's battery is not depleted. Reset is only allowed for depleted pets."
                )
                
            # Delete the old pet
            await PetDB.delete_pet(str(pet.id))
        
        # Create a new pet for the user
        new_pet_data = {
            "name": "Berny", # Default name, can be customized later
            "species": "Digital",
            "mood": MOOD_LEVELS["HAPPY"],
            "level": 1,
            "sassLevel": SASS_LEVELS["SWEET"],
            "batteryLevel": 100,
            "userId": str(current_user.id),
            "lastFed": datetime.now(timezone.utc),
            "lastInteraction": datetime.now(timezone.utc),
            "interactionCount": 0,
            "memoryLog": ["I was just created! Hello world!"]
        }
        
        # Create the new pet
        new_pet = await PetDB.create_pet(new_pet_data)
        
        if not new_pet:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create new pet"
            )
            
        # Ensure the pet has both id and _id for frontend compatibility
        new_pet_dict = new_pet.model_dump()
        if '_id' in new_pet_dict and not new_pet_dict.get('id'):
            new_pet_dict['id'] = new_pet_dict['_id']
        
        print(f"[API] Reset successful. Created new pet ID: {new_pet_dict.get('id') or new_pet_dict.get('_id')}")
        return new_pet_dict
    except Exception as e:
        print(f"[API] Error in reset_pet: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset pet: {str(e)}"
        )

# Test endpoint
@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is running"""
    return {"status": "ok", "message": "API is running"}

# MongoDB test endpoint
@router.get("/test-mongodb")
async def test_mongodb():
    """Test endpoint to verify MongoDB connection"""
    try:
        # Try to get a pet - doesn't matter if it exists, just testing the connection
        pet = await PetDB.get_pets_by_user("test")
        return {
            "status": "ok", 
            "message": "MongoDB connection successful",
            "connection_info": {
                "database": os.getenv("MONGODB_DB_NAME"),
                "uri": "...@" + (os.getenv("MONGODB_URI") or "").split("@")[-1] if "@" in (os.getenv("MONGODB_URI") or "") else "Not configured"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(e)}") 