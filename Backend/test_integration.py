import unittest
import os
import sys
from fastapi.testclient import TestClient
from api.main import app
from database.database import async_pets_collection, async_users_collection, PetDB, UserDB
from database.pet_schema import Pet
from database.user_schema import UserCreate
from api.ai_personality import get_chronopal_response
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestBackendIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_ai_personality(self):
        """Test the AI personality responses"""
        test_cases = [
            ("hello", "happy", 1, 1),
            ("how are you?", "excited", 3, 2),
            ("what's your favorite food?", "default", 2, 3),
        ]
        
        for message, mood, level, sass_level in test_cases:
            response = get_chronopal_response(message, mood, level, sass_level)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
    
    @pytest.mark.asyncio
    async def test_user_creation(self):
        """Test user creation and retrieval"""
        # Create test user
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password"
        }
        
        user = UserCreate(**user_data)
        created_user = await UserDB.create_user(user)
        
        # Retrieve user
        retrieved_user = await UserDB.get_user_by_id(str(created_user.id))
        self.assertEqual(retrieved_user.username, user_data["username"])
    
    @pytest.mark.asyncio
    async def test_pet_creation(self):
        """Test pet creation and interaction"""
        # Create test pet
        pet_data = {
            "name": "TestPet",
            "species": "cat",
            "mood": "happy",
            "level": 1,
            "sass_level": 1
        }
        
        pet = Pet(**pet_data)
        created_pet = await PetDB.create_pet(pet)
        
        # Test pet interaction
        interaction_data = {
            "message": "Hello pet!",
            "mood": "happy",
            "level": 1,
            "sass_level": 1
        }
        
        response = get_chronopal_response(
            interaction_data["message"],
            interaction_data["mood"],
            interaction_data["level"],
            interaction_data["sass_level"]
        )
        self.assertIsInstance(response, str)
    
    @pytest.mark.asyncio
    async def test_full_integration(self):
        """Test full system integration"""
        # Create user
        user_data = {
            "username": "integration_test_user",
            "email": "integration@example.com",
            "password": "test_password"
        }
        user = UserCreate(**user_data)
        created_user = await UserDB.create_user(user)
        
        # Create pet for user
        pet_data = {
            "name": "IntegrationPet",
            "species": "dog",
            "mood": "excited",
            "level": 1,
            "sass_level": 1,
            "userId": str(created_user.id)
        }
        pet = Pet(**pet_data)
        created_pet = await PetDB.create_pet(pet)
        
        # Interact with pet
        interaction_data = {
            "message": "What's your favorite toy?",
            "mood": "excited",
            "level": 1,
            "sass_level": 1
        }
        response = get_chronopal_response(
            interaction_data["message"],
            interaction_data["mood"],
            interaction_data["level"],
            interaction_data["sass_level"]
        )
        
        # Verify all responses
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == "__main__":
    unittest.main() 