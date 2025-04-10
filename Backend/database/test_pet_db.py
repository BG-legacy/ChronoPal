import asyncio
from datetime import datetime
from database.pet_schema import Pet
from database.database import PetDB

async def test_pet_operations():
    print("Starting Pet Database Tests...")
    
    # Test 1: Create a new pet
    print("\nTest 1: Creating a new pet...")
    new_pet = Pet(
        userId="test_user_123",
        petName="TestPet",
        level=1,
        mood="happy",
        evolutionStage="baby"
    )
    created_pet = await PetDB.create_pet(new_pet)
    print(f"Created pet: {created_pet.model_dump()}")
    
    # Test 2: Get the created pet
    print("\nTest 2: Getting the created pet...")
    retrieved_pet = await PetDB.get_pet(created_pet.id)
    print(f"Retrieved pet: {retrieved_pet.model_dump()}")
    
    # Test 3: Update pet's mood
    print("\nTest 3: Updating pet's mood...")
    updated_pet = await PetDB.update_mood(created_pet.id, "excited")
    print(f"Updated pet mood: {updated_pet.model_dump()}")
    
    # Test 4: Add a memory
    print("\nTest 4: Adding a memory...")
    memory_pet = await PetDB.add_memory(created_pet.id, "First test memory!")
    print(f"Pet with new memory: {memory_pet.model_dump()}")
    
    # Test 5: Update level
    print("\nTest 5: Updating level...")
    leveled_pet = await PetDB.update_level(created_pet.id, 2)
    print(f"Pet with updated level: {leveled_pet.model_dump()}")
    
    # Test 6: Get all pets for user
    print("\nTest 6: Getting all pets for user...")
    user_pets = await PetDB.get_pets_by_user("test_user_123")
    print(f"User's pets: {[pet.model_dump() for pet in user_pets]}")
    
    # Test 7: Delete the pet
    print("\nTest 7: Deleting the pet...")
    delete_result = await PetDB.delete_pet(created_pet.id)
    print(f"Delete successful: {delete_result}")
    
    # Verify deletion
    print("\nVerifying deletion...")
    deleted_pet = await PetDB.get_pet(created_pet.id)
    print(f"Pet should be None: {deleted_pet}")

if __name__ == "__main__":
    asyncio.run(test_pet_operations()) 