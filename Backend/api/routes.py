from fastapi import APIRouter, HTTPException, Depends, status, Header
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
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

class InteractionRequest(BaseModel):
    pet_id: str
    interaction_type: str  # "feed", "play", or "teach"
    message: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    pet_id: str

async def get_current_user(session_id: str = Header(None, alias="session-id")):
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_id = active_sessions.get(session_id)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    user = await UserDB.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
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
    user = await UserDB.get_user_by_email(user_login.email)
    if not user or not UserDB.verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create a simple session (in production, use proper session management)
    session_id = str(os.urandom(16).hex())
    active_sessions[session_id] = str(user.id)
    
    return {"session_id": session_id}

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
    """Fetch user's saved pet"""
    try:
        pets = await PetDB.get_pets_by_user(str(current_user.id))
        if not pets:
            raise HTTPException(status_code=404, detail="No pet found for this user")
        return pets[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/update-interaction")
async def update_interaction(interaction: InteractionRequest, current_user: User = Depends(get_current_user)):
    """Update pet based on interaction type"""
    try:
        pet = await PetDB.get_pet(interaction.pet_id)
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        if pet.userId != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to interact with this pet")

        # Update based on interaction type
        if interaction.interaction_type == "feed":
            await PetDB.update_last_fed(interaction.pet_id)
            await PetDB.update_mood(interaction.pet_id, "happy")
        elif interaction.interaction_type == "play":
            await PetDB.update_mood(interaction.pet_id, "excited")
        elif interaction.interaction_type == "teach":
            if interaction.message:
                await PetDB.add_memory(interaction.pet_id, interaction.message)
                await PetDB.update_level(interaction.pet_id, pet.level + 1)
        else:
            raise HTTPException(status_code=400, detail="Invalid interaction type")

        # Increment interaction count
        await PetDB.increment_interaction(interaction.pet_id)
        
        updated_pet = await PetDB.get_pet(interaction.pet_id)
        if not updated_pet:
            raise HTTPException(status_code=404, detail="Pet not found after update")
        return updated_pet
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/save-pet", response_model=Pet)
async def save_pet(pet: Pet, current_user: User = Depends(get_current_user)):
    """Save pet data to database"""
    try:
        # Remove _id if it exists to let MongoDB generate it
        pet_dict = pet.model_dump(by_alias=True)
        if "_id" in pet_dict:
            del pet_dict["_id"]
        
        pet_dict["userId"] = str(current_user.id)  # Ensure pet is associated with current user
        saved_pet = await PetDB.create_pet(pet_dict)
        return saved_pet
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/chat")
async def chat_with_pet(chat_request: ChatRequest, current_user: User = Depends(get_current_user)):
    """Handle chat with pet using AI personality"""
    try:
        # Get pet context
        pet = await PetDB.get_pet(chat_request.pet_id)
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        if pet.userId != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to chat with this pet")

        # Calculate sass level based on pet's level and existing sass_level
        sass_level = pet.sass_level

        # Get AI response based on pet's state and user message
        response = get_chronopal_response(
            user_message=chat_request.message,
            pet_mood=pet.mood,
            pet_level=pet.level,
            sass_level=sass_level
        )

        # Add the interaction to pet's memory and increment interaction count
        await PetDB.add_memory(chat_request.pet_id, f"User: {chat_request.message}")
        await PetDB.add_memory(chat_request.pet_id, f"Pet: {response}")
        await PetDB.increment_interaction(chat_request.pet_id)

        return {"response": response}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 