#!/usr/bin/env python
"""
Direct Pet Interaction Test.
Bypasses the API to directly test database operations.
"""

import asyncio
import os
import sys
from database.database import PetDB
from database.pet_schema import Pet
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PET_ID = "67f85f50337e5e21bf3e6328"  # The ID we found earlier

async def test_direct_interaction():
    """Test direct interaction with the pet in the database"""
    print(f"\n=== Testing Direct Interaction with Pet ID: {PET_ID} ===\n")
    
    # 1. Retrieve the pet
    print("Step 1: Retrieving pet...")
    pet = await PetDB.get_pet(PET_ID)
    if not pet:
        print(f"❌ Error: Pet not found with ID {PET_ID}")
        return False
    
    print(f"✅ Found pet: {pet.name}")
    print(f"   Level: {pet.level}")
    print(f"   Mood: {pet.mood}")
    print(f"   Interactions: {pet.interactionCount}")
    
    # 2. Update the mood
    print("\nStep 2: Updating mood...")
    updated_pet = await PetDB.update_mood(PET_ID, "excited")
    if not updated_pet:
        print("❌ Error: Failed to update mood")
        return False
    
    print(f"✅ Updated mood to: {updated_pet.mood}")
    
    # 3. Increment interaction
    print("\nStep 3: Incrementing interaction count...")
    updated_pet = await PetDB.increment_interaction(PET_ID)
    if not updated_pet:
        print("❌ Error: Failed to increment interaction")
        return False
    
    print(f"✅ Incremented interaction count to: {updated_pet.interactionCount}")
    
    # 4. Feed the pet
    print("\nStep 4: Feeding pet...")
    updated_pet = await PetDB.update_last_fed(PET_ID)
    if not updated_pet:
        print("❌ Error: Failed to feed pet")
        return False
    
    print(f"✅ Updated last fed time to: {updated_pet.lastFed}")
    
    # 5. Add a memory
    print("\nStep 5: Adding a memory...")
    memory = "Direct interaction test via script"
    updated_pet = await PetDB.add_memory(PET_ID, memory)
    if not updated_pet:
        print("❌ Error: Failed to add memory")
        return False
    
    print(f"✅ Added memory: '{memory}'")
    print(f"   Memory log now has {len(updated_pet.memoryLog)} entries")
    
    print("\n=== All tests passed successfully! ===")
    return True

if __name__ == "__main__":
    asyncio.run(test_direct_interaction()) 