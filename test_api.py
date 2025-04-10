from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, UTC
from api.main import app
from database.user_schema import UserCreate, UserLogin
from database.pet_schema import Pet
from database.database import UserDB, PetDB
import pytest

# Configure test database
TEST_MONGODB_URI = "mongodb://localhost:27017"
TEST_DB_NAME = "test_chronopal"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create a test database and handle cleanup."""
    client = AsyncIOMotorClient(TEST_MONGODB_URI)
    db = client[TEST_DB_NAME]
    
    # Clear database before tests
    await db.users.delete_many({})
    await db.pets.delete_many({})
    
    yield db
    
    # Cleanup after tests
    await db.users.delete_many({})
    await db.pets.delete_many({})
    await client.close()

@pytest.fixture
async def test_client(test_db):
    """Create a test client with the test database."""
    app.state.mongodb = AsyncIOMotorClient(TEST_MONGODB_URI)
    app.state.db = test_db
    async with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
async def clean_db(test_db):
    """Clean the database before each test."""
    await test_db.users.delete_many({})
    await test_db.pets.delete_many({})

# Test data
TEST_USER = UserCreate(
    email="test@example.com",
    password="testpass123",
    username="testuser"
)

TEST_PET = Pet(
    id="",  # Will be set during test
    userId="",  # Will be set during test
    petName="TestPet",
    species="cat",
    mood="happy",
    level=1,
    evolutionStage="baby",
    lastFed=datetime.now(UTC),
    memoryLog=[],
    sassLevel=5,
    interactionCount=0
)

@pytest.mark.asyncio
async def test_save_pet(test_client):
    # Register and login first
    register_response = await test_client.post("/api/register", json=TEST_USER.model_dump())
    user_id = register_response.json()["id"]
    login_data = UserLogin(email=TEST_USER.email, password=TEST_USER.password)
    login_response = await test_client.post("/api/login", json=login_data.model_dump())
    session_id = login_response.json()["session_id"]
    
    # Update TEST_PET with user_id
    test_pet_data = TEST_PET.model_dump()
    test_pet_data["userId"] = user_id
    
    # Save pet
    response = await test_client.post(
        "/api/save-pet",
        json=test_pet_data,
        headers={"session-id": session_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["userId"] == user_id
    assert data["petName"] == TEST_PET.petName

@pytest.mark.asyncio
async def test_update_interaction(test_client):
    # Register and login first
    register_response = await test_client.post("/api/register", json=TEST_USER.model_dump())
    user_id = register_response.json()["id"]
    login_data = UserLogin(email=TEST_USER.email, password=TEST_USER.password)
    login_response = await test_client.post("/api/login", json=login_data.model_dump())
    session_id = login_response.json()["session_id"]
    
    # Save pet first
    test_pet_data = TEST_PET.model_dump()
    test_pet_data["userId"] = user_id
    pet_response = await test_client.post(
        "/api/save-pet",
        json=test_pet_data,
        headers={"session-id": session_id}
    )
    pet_id = pet_response.json()["id"]
    
    # Update interaction
    interaction_data = {
        "pet_id": pet_id,
        "interaction_type": "feed",
        "message": None
    }
    response = await test_client.post(
        "/api/update-interaction",
        json=interaction_data,
        headers={"session-id": session_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mood"] == "happy"

@pytest.mark.asyncio
async def test_chat_with_pet(test_client):
    # Register and login first
    register_response = await test_client.post("/api/register", json=TEST_USER.model_dump())
    user_id = register_response.json()["id"]
    login_data = UserLogin(email=TEST_USER.email, password=TEST_USER.password)
    login_response = await test_client.post("/api/login", json=login_data.model_dump())
    session_id = login_response.json()["session_id"]
    
    # Save pet first
    test_pet_data = TEST_PET.model_dump()
    test_pet_data["userId"] = user_id
    pet_response = await test_client.post(
        "/api/save-pet",
        json=test_pet_data,
        headers={"session-id": session_id}
    )
    pet_id = pet_response.json()["id"]
    
    # Chat with pet
    chat_data = {
        "message": "Hello pet!",
        "pet_id": pet_id
    }
    response = await test_client.post(
        "/api/chat",
        json=chat_data,
        headers={"session-id": session_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)

@pytest.mark.asyncio
async def test_register_user(test_client):
    """Test user registration."""
    response = await test_client.post("/api/register", json=TEST_USER.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == TEST_USER.email
    assert data["username"] == TEST_USER.username

@pytest.mark.asyncio
async def test_register_duplicate_user(test_client):
    """Test registering a user with an existing email."""
    # First registration
    await test_client.post("/api/register", json=TEST_USER.model_dump())
    # Second registration with same email
    response = await test_client.post("/api/register", json=TEST_USER.model_dump())
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(test_client):
    """Test successful login."""
    # Register user first
    await test_client.post("/api/register", json=TEST_USER.model_dump())
    # Try to login
    login_data = UserLogin(email=TEST_USER.email, password=TEST_USER.password)
    response = await test_client.post("/api/login", json=login_data.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data

@pytest.mark.asyncio
async def test_login_failure(test_client):
    """Test login with incorrect credentials."""
    login_data = UserLogin(email="wrong@example.com", password="wrongpass")
    response = await test_client.post("/api/login", json=login_data.model_dump())
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_logout(test_client):
    """Test user logout."""
    # Register and login first
    await test_client.post("/api/register", json=TEST_USER.model_dump())
    login_data = UserLogin(email=TEST_USER.email, password=TEST_USER.password)
    login_response = await test_client.post("/api/login", json=login_data.model_dump())
    session_id = login_response.json()["session_id"]
    
    # Test logout
    response = await test_client.post("/api/logout", params={"session_id": session_id})
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully" 