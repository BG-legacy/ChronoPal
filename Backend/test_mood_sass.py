import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from database.pet_schema import Pet, MOOD_LEVELS, SASS_LEVELS, NEGLECT_THRESHOLD_HOURS
from database.database import PetDB, async_client, async_db, async_pets_collection
import motor.motor_asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_connection():
    """Create a fresh database connection for the test session."""
    # The connection is already established in database.py
    yield async_db

@pytest.fixture(scope="function")
async def setup_teardown(db_connection):
    """Setup and teardown for each test."""
    # Setup - nothing needed
    yield
    
    # Teardown - Clean up test pets
    try:
        await async_pets_collection.delete_many({"userId": "test_user"})
    except Exception as e:
        print(f"Error in teardown: {str(e)}")

@pytest.mark.asyncio
async def test_neglect_effects(setup_teardown):
    # Create a test pet
    pet_data = {
        "name": "TestPet",
        "species": "cat",
        "userId": "test_user",
        "lastInteraction": datetime.now(timezone.utc) - timedelta(hours=NEGLECT_THRESHOLD_HOURS + 1)
    }
    pet = await PetDB.create_pet(pet_data)
    
    # Check initial state
    assert pet.mood == MOOD_LEVELS["HAPPY"]
    assert pet.sass_level == SASS_LEVELS["SWEET"]
    assert pet.level == 1
    
    # Check neglect
    updated_pet = await PetDB.check_neglect(pet.id)
    assert updated_pet.mood == MOOD_LEVELS["GRUMPY"]
    assert updated_pet.sass_level == SASS_LEVELS["PLAYFUL"]  # Increased by 1
    assert updated_pet.level == 1  # Should stay at 1 since it's the minimum
    
    # Check memory log
    assert len(updated_pet.memoryLog) > 0
    assert "neglected" in updated_pet.memoryLog[0].lower()

@pytest.mark.asyncio
async def test_multiple_neglect_periods(setup_teardown):
    # Create a test pet with longer neglect
    pet_data = {
        "name": "TestPet2",
        "species": "cat",
        "userId": "test_user",
        "lastInteraction": datetime.now(timezone.utc) - timedelta(hours=NEGLECT_THRESHOLD_HOURS * 3)
    }
    pet = await PetDB.create_pet(pet_data)
    
    # Check neglect effects
    updated_pet = await PetDB.check_neglect(pet.id)
    assert updated_pet.mood == MOOD_LEVELS["GRUMPY"]
    assert updated_pet.sass_level == SASS_LEVELS["SNARKY"]  # Increased by 2 due to 3 neglect periods
    assert updated_pet.level == 1  # Should stay at 1 since it's the minimum

@pytest.mark.asyncio
async def test_sass_level_progression(setup_teardown):
    # Create a test pet
    pet_data = {
        "name": "TestPet3",
        "species": "cat",
        "userId": "test_user"
    }
    pet = await PetDB.create_pet(pet_data)
    
    # Simulate multiple interactions
    for _ in range(15):  # Should reach PLAYFUL level
        pet = await PetDB.increment_interaction(pet.id)
    
    assert pet.sass_level == SASS_LEVELS["PLAYFUL"]
    
    # More interactions to reach SNARKY
    for _ in range(25):
        pet = await PetDB.increment_interaction(pet.id)
    
    assert pet.sass_level == SASS_LEVELS["SNARKY"]
    
    # More interactions to reach SASSY
    for _ in range(50):
        pet = await PetDB.increment_interaction(pet.id)
    
    assert pet.sass_level == SASS_LEVELS["SASSY"]
    
    # More interactions to reach SAVAGE
    for _ in range(100):
        pet = await PetDB.increment_interaction(pet.id)
    
    assert pet.sass_level == SASS_LEVELS["SAVAGE"]

@pytest.mark.asyncio
async def test_interaction_resets_neglect(setup_teardown):
    # Create a neglected pet
    pet_data = {
        "name": "TestPet4",
        "species": "cat",
        "userId": "test_user",
        "lastInteraction": datetime.now(timezone.utc) - timedelta(hours=NEGLECT_THRESHOLD_HOURS + 1)
    }
    pet = await PetDB.create_pet(pet_data)
    
    # Verify neglect effects
    pet = await PetDB.check_neglect(pet.id)
    assert pet.mood == MOOD_LEVELS["GRUMPY"]
    
    # Interact with pet and ensure lastInteraction is updated
    before_interaction = datetime.now(timezone.utc)
    pet = await PetDB.increment_interaction(pet.id)
    after_interaction = datetime.now(timezone.utc)
    
    # Ensure lastInteraction is timezone-aware
    if pet.lastInteraction.tzinfo is None:
        pet.lastInteraction = pet.lastInteraction.replace(tzinfo=timezone.utc)
    
    # Check that lastInteraction was updated within the test execution window
    assert before_interaction <= pet.lastInteraction <= after_interaction 