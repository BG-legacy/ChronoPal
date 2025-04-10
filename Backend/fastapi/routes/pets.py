from fastapi import APIRouter, HTTPException
from fastapi.db import db
from fastapi.models import Pet
from datetime import datetime

router = APIRouter()

# Route to get a user's pet
@router.get("/pets/{user_id}", response_model=Pet)
async def get_pet(user_id: str):
    pet = await db.pets.find_one({"userId": user_id})
    if pet:
        return pet
    raise HTTPException(status_code=404, detail="Pet not found")

# Route to update pet interaction (feed/play/teach)
@router.post("/pets/update-interaction", response_model=Pet)
async def update_pet_interaction(user_id: str, action: str):
    pet = await db.pets.find_one({"userId": user_id})
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Logic to update pet state
    if action == "feed":
        pet["lastFed"] = datetime.utcnow()
        pet["mood"] = "happy"  # Change mood after feeding
    elif action == "play":
        pet["mood"] = "excited"  # Change mood after playing
    elif action == "teach":
        pet["memoryLog"].append("New tech fact learned!")  # Add memory log after teaching

    # Save the updated pet back to the database
    await db.pets.replace_one({"userId": user_id}, pet)
    
    return pet
