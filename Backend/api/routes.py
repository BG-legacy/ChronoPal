from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from database.pet_schema import Pet
from database.user_schema import User, UserCreate, UserLogin
from database.database import PetDB, UserDB
from .ai_personality import get_chronopal_response
from bson import ObjectId

# Load environment variables
load_dotenv()

router = APIRouter()

# Store active sessions (in production, use a proper session store)
active_sessions = {}

# Function to set the active_sessions from main.py
def set_active_sessions(sessions_dict):
    """Set the active sessions dictionary from the main app"""
    global active_sessions
    active_sessions = sessions_dict
    print(f"Session store initialized with {len(active_sessions)} existing sessions")

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
    print(f"[AUTH DEBUG] Active sessions: {list(active_sessions.keys())[:5] if active_sessions else 'None'}")
    
    user_id = active_sessions.get(session_id)
    if not user_id:
        print(f"[AUTH ERROR] Session ID not found in active sessions: {session_id[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    print(f"[AUTH DEBUG] Found user_id: {user_id} for session: {session_id[:8]}...")
    
    user = await UserDB.get_user_by_id(user_id)
    if not user:
        print(f"[AUTH ERROR] User not found for ID: {user_id}")
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
    
    # Create a simple session (in production, use proper session management)
    session_id = str(os.urandom(16).hex())
    active_sessions[session_id] = str(user.id)
    
    print(f"[LOGIN SUCCESS] Created session {session_id[:8]}... for user {user.username} (ID: {user.id})")
    print(f"[SESSION DEBUG] Total active sessions: {len(active_sessions)}")
    
    return {"session_id": session_id, "user": user}

@router.post("/logout")
async def logout(session_id: str = Header(None, alias="session-id")):
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if session_id in active_sessions:
        del active_sessions[session_id]
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
    """Feed the user's first pet, fetching it directly from user's pets"""
    try:
        print(f"Received feed-pet-by-user request for user: {current_user.id}")
        
        # Get all of the user's pets
        pets = await PetDB.get_pets_by_user(str(current_user.id))
        
        if not pets or len(pets) == 0:
            print(f"No pets found for user: {current_user.id}")
            raise HTTPException(status_code=404, detail="No pets found for user")
        
        # Use the first pet (users currently only have one pet)
        pet = pets[0]
        pet_id = str(pet.id)
        
        print(f"Found pet with ID: {pet_id}, Name: {pet.name}, User: {pet.userId}")
        
        # Update this specific pet
        updated_pet = await PetDB.feed_pet(pet_id)
        
        if not updated_pet:
            print(f"Failed to update pet: {pet_id}")
            raise HTTPException(status_code=500, detail="Failed to update pet")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"Feed interaction successful. Updated pet ID: {updated_pet_dict.get('id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"Error in feed_pet_by_user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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
    """Play with the user's first pet, fetching it directly from user's pets"""
    try:
        print(f"Received play-with-pet-by-user request for user: {current_user.id}")
        
        # Get all of the user's pets
        pets = await PetDB.get_pets_by_user(str(current_user.id))
        
        if not pets or len(pets) == 0:
            print(f"No pets found for user: {current_user.id}")
            raise HTTPException(status_code=404, detail="No pets found for user")
        
        # Use the first pet (users currently only have one pet)
        pet = pets[0]
        pet_id = str(pet.id)
        
        print(f"Found pet with ID: {pet_id}, Name: {pet.name}, User: {pet.userId}")
        
        # Update this specific pet
        updated_pet = await PetDB.play_with_pet(pet_id)
        
        if not updated_pet:
            print(f"Failed to update pet: {pet_id}")
            raise HTTPException(status_code=500, detail="Failed to update pet")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"Play interaction successful. Updated pet ID: {updated_pet_dict.get('id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"Error in play_with_pet_by_user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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
    """Teach the user's first pet, fetching it directly from user's pets"""
    try:
        message = request.message
        print(f"Received teach-pet-by-user request for user: {current_user.id}, message: {message}")
        
        if not message or message.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message is required for 'teach' interactions"
            )
        
        # Get all of the user's pets
        pets = await PetDB.get_pets_by_user(str(current_user.id))
        
        if not pets or len(pets) == 0:
            print(f"No pets found for user: {current_user.id}")
            raise HTTPException(status_code=404, detail="No pets found for user")
        
        # Use the first pet (users currently only have one pet)
        pet = pets[0]
        pet_id = str(pet.id)
        
        print(f"Found pet with ID: {pet_id}, Name: {pet.name}, User: {pet.userId}")
        
        # Update this specific pet
        updated_pet = await PetDB.teach_pet(pet_id, message)
        
        if not updated_pet:
            print(f"Failed to update pet: {pet_id}")
            raise HTTPException(status_code=500, detail="Failed to update pet")
        
        # Ensure the pet has both id and _id for frontend compatibility
        updated_pet_dict = updated_pet.model_dump()
        if '_id' in updated_pet_dict and not updated_pet_dict.get('id'):
            updated_pet_dict['id'] = updated_pet_dict['_id']
        
        print(f"Teach interaction successful. Updated pet ID: {updated_pet_dict.get('id')}")
        return updated_pet_dict
    except Exception as e:
        print(f"Error in teach_pet_by_user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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
    """Handle chat with pet using AI personality"""
    try:
        print(f"[CHAT] Received chat request from user {current_user.id} for pet {chat_request.pet_id}")
        
        # First, try to get the pet by the provided ID
        pet = None
        try:
            pet = await PetDB.get_pet(chat_request.pet_id)
            if pet and pet.userId == str(current_user.id):
                print(f"[CHAT] Found pet with provided ID: {pet.id}, belongs to user {pet.userId}")
            else:
                print(f"[CHAT] Pet not found or doesn't belong to user: {chat_request.pet_id}")
                pet = None
        except Exception as pet_err:
            print(f"[CHAT] Error finding pet with ID {chat_request.pet_id}: {str(pet_err)}")
            pet = None
        
        # If pet not found or doesn't belong to user, try to find user's pets
        if not pet:
            print(f"[CHAT] Looking for alternative pets for user {current_user.id}")
            
            # Get all pets for this user
            try:
                user_pets = await PetDB.get_pets_by_user(current_user.id)
                
                if not user_pets:
                    print(f"[CHAT] No pets found for user {current_user.id}")
                    raise HTTPException(status_code=404, detail="No pets found for this user")
                
                # Use the first pet (same as fixed-pet endpoint)
                pet = user_pets[0]
                print(f"[CHAT] Using alternative pet with ID: {pet.id}")
            except Exception as user_pet_err:
                print(f"[CHAT] Error finding user's pets: {str(user_pet_err)}")
                raise HTTPException(status_code=404, detail="Could not find any pets for this user")
        
        # Calculate sass level based on pet's level and existing sass_level
        sass_level = pet.sassLevel

        # Get AI response based on pet's state and user message
        response = get_chronopal_response(
            user_message=chat_request.message,
            pet_mood=pet.mood,
            pet_level=pet.level,
            sass_level=sass_level
        )

        # Add the interaction to pet's memory and increment interaction count
        await PetDB.add_memory(pet.id, f"User: {chat_request.message}")
        await PetDB.add_memory(pet.id, f"Pet: {response}")
        await PetDB.increment_interaction(pet.id)

        return {"response": response}
    except Exception as e:
        print(f"[CHAT ERROR] {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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