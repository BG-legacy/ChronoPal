import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.database import async_pets_collection, async_users_collection, PetDB, UserDB
from database.pet_schema import Pet
from database.user_schema import UserCreate
import os
from dotenv import load_dotenv
import asyncio
from httpx import AsyncClient
from bson import ObjectId
from datetime import datetime, timezone
from unittest.mock import patch

# Load environment variables
load_dotenv()

# Mock AI response for testing
def mock_get_chronopal_response(*args, **kwargs):
    return "Test response from ChronoPal"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """Create an async client for testing."""
    base_url = "http://test"
    async with AsyncClient(app=app, base_url=base_url) as client:
        yield client

@pytest.fixture
async def test_user():
    # First, ensure no existing user with the test email
    existing_user = await UserDB.get_user_by_email("test_endpoints@example.com")
    if existing_user:
        # Clean up any existing pets for this user
        existing_pets = await PetDB.get_pets_by_user(str(existing_user.id))
        for pet in existing_pets:
            await async_pets_collection.delete_one({"_id": ObjectId(pet.id)})
        # Delete the user
        await async_users_collection.delete_one({"_id": ObjectId(existing_user.id)})
    
    # Create a test user
    user_data = {
        "username": "test_user_endpoints",
        "email": "test_endpoints@example.com",
        "password": "test_password"
    }
    user = UserCreate(**user_data)
    created_user = await UserDB.create_user(user)
    yield created_user
    # Cleanup
    # Clean up any pets for this user
    existing_pets = await PetDB.get_pets_by_user(str(created_user.id))
    for pet in existing_pets:
        await async_pets_collection.delete_one({"_id": ObjectId(pet.id)})
    # Delete the user
    await async_users_collection.delete_one({"_id": ObjectId(created_user.id)})

@pytest.fixture
async def test_pet(test_user):
    # First, ensure no existing pets for the test user
    existing_pets = await PetDB.get_pets_by_user(str(test_user.id))
    for pet in existing_pets:
        await async_pets_collection.delete_one({"_id": ObjectId(pet.id)})
    
    # Create a test pet with all required fields
    pet_data = Pet(
        name="TestPet",
        species="cat",
        mood="happy",
        level=1,
        sass_level=1,
        userId=str(test_user.id),
        lastFed=datetime.now(timezone.utc),
        interactionCount=0,
        memoryLog=[]
    )
    created_pet = await PetDB.create_pet(pet_data)
    
    # Verify the pet was created with the correct user ID
    assert created_pet.userId == str(test_user.id)
    
    yield created_pet
    # Cleanup
    await async_pets_collection.delete_one({"_id": ObjectId(created_pet.id)})

@pytest.mark.asyncio
async def test_register_endpoint(async_client):
    # First, ensure no existing user with the test email
    existing_user = await UserDB.get_user_by_email("new_test@example.com")
    if existing_user:
        # Clean up any existing pets for this user
        existing_pets = await PetDB.get_pets_by_user(str(existing_user.id))
        for pet in existing_pets:
            await async_pets_collection.delete_one({"_id": ObjectId(pet.id)})
        # Delete the user
        await async_users_collection.delete_one({"_id": ObjectId(existing_user.id)})
    
    # Test user registration
    response = await async_client.post("/api/register", json={
        "username": "new_test_user",
        "email": "new_test@example.com",
        "password": "new_password"
    })
    assert response.status_code == 200
    data = response.json()
    assert "_id" in data
    assert data["username"] == "new_test_user"
    assert data["email"] == "new_test@example.com"
    # Cleanup
    # Clean up any pets for this user
    existing_pets = await PetDB.get_pets_by_user(str(data["_id"]))
    for pet in existing_pets:
        await async_pets_collection.delete_one({"_id": ObjectId(pet.id)})
    # Delete the user
    await async_users_collection.delete_one({"_id": ObjectId(data["_id"])})

@pytest.mark.asyncio
async def test_login_endpoint(async_client, test_user):
    # Test login
    response = await async_client.post("/api/login", json={
        "email": "test_endpoints@example.com",
        "password": "test_password"
    })
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    return data["session_id"]

@pytest.mark.asyncio
async def test_logout_endpoint(async_client, test_user):
    # First login to get a session
    session_id = await test_login_endpoint(async_client, test_user)
    
    # Test logout
    response = await async_client.post("/api/logout", headers={"session-id": session_id})
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"

@pytest.mark.asyncio
async def test_user_pet_endpoint(async_client, test_user, test_pet):
    # Login first
    session_id = await test_login_endpoint(async_client, test_user)
    
    # Test getting user's pet
    response = await async_client.get("/api/user-pet", headers={"session-id": session_id})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestPet"
    assert data["species"] == "cat"
    assert data["userId"] == str(test_user.id)

@pytest.mark.asyncio
async def test_update_interaction_endpoint(async_client, test_user, test_pet):
    # Login first
    session_id = await test_login_endpoint(async_client, test_user)
    
    # Test feeding interaction
    response = await async_client.post("/api/update-interaction", 
        headers={"session-id": session_id},
        json={
            "pet_id": str(test_pet.id),
            "interaction_type": "feed"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mood"] == "happy"
    assert data["userId"] == str(test_user.id)

    # Test play interaction
    response = await async_client.post("/api/update-interaction", 
        headers={"session-id": session_id},
        json={
            "pet_id": str(test_pet.id),
            "interaction_type": "play"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mood"] == "excited"
    assert data["userId"] == str(test_user.id)

    # Test teach interaction
    response = await async_client.post("/api/update-interaction", 
        headers={"session-id": session_id},
        json={
            "pet_id": str(test_pet.id),
            "interaction_type": "teach",
            "message": "Learn to sit"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 2  # Level should increase by 1
    assert data["userId"] == str(test_user.id)

@pytest.mark.asyncio
async def test_save_pet_endpoint(async_client, test_user):
    # Login first
    session_id = await test_login_endpoint(async_client, test_user)
    
    # Test saving a new pet
    response = await async_client.post("/api/save-pet", 
        headers={"session-id": session_id},
        json={
            "name": "NewPet",
            "species": "dog",
            "mood": "excited",
            "level": 1,
            "sass_level": 1,
            "userId": str(test_user.id),
            "lastFed": datetime.now(timezone.utc).isoformat(),
            "interactionCount": 0,
            "memoryLog": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NewPet"
    assert data["species"] == "dog"
    assert data["userId"] == str(test_user.id)
    # Cleanup
    await async_pets_collection.delete_one({"_id": ObjectId(data["_id"])})

@pytest.mark.asyncio
@patch('api.routes.get_chronopal_response', side_effect=mock_get_chronopal_response)
async def test_chat_endpoint(mock_response, async_client, test_user, test_pet):
    # Login first
    session_id = await test_login_endpoint(async_client, test_user)
    
    # Test chatting with pet
    response = await async_client.post("/api/chat", 
        headers={"session-id": session_id},
        json={
            "message": "Hello pet!",
            "pet_id": str(test_pet.id)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0 