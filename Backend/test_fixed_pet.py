#!/usr/bin/env python
"""
Script to test the fixed-pet endpoint for consistency
"""

import asyncio
import os
import sys
import requests
from database.database import PetDB, UserDB, async_users_collection
from database.pet_schema import Pet
from dotenv import load_dotenv
import json
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL") or "http://localhost:8000"

# We'll create a test user with a known password
TEST_EMAIL = "test@chronopal.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"

async def create_test_user():
    """Create a test user if it doesn't exist"""
    user = await UserDB.get_user_by_email(TEST_EMAIL)
    if user:
        print(f"\nUsing existing test user: {user.username}")
        return user
    
    from database.user_schema import UserCreate
    from passlib.context import CryptContext
    
    # Create new user directly
    print(f"\nCreating test user: {TEST_USERNAME}")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(TEST_PASSWORD)
    
    user_dict = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await async_users_collection.insert_one(user_dict)
    created_user = await async_users_collection.find_one({"_id": result.inserted_id})
    if created_user:
        created_user["_id"] = str(created_user["_id"])
        from database.user_schema import User
        return User(**created_user)
    return None

async def find_valid_user():
    """Find a valid user and print their details"""
    users = []
    async for user in async_users_collection.find({}):
        if user:
            user["_id"] = str(user["_id"])
            users.append(user)
            
    if users:
        print(f"\nFound {len(users)} users in database")
        for i, user in enumerate(users[:3]):  # Show first 3 users
            print(f"\nUser {i+1}: {user.get('username', 'Unknown')}")
            print(f"  Email: {user.get('email', 'Unknown')}")
            print(f"  ID: {user.get('_id', 'Unknown')}")
        
        # Return the first user's email
        return users[0].get('email', None)
    
    return None

async def get_all_pets_for_user(user_id):
    """Get all pets for a user directly from database"""
    pets = await PetDB.get_pets_by_user(user_id)
    print(f"\n== Pets for User {user_id} in Database ({len(pets)}) ==")
    
    for i, pet in enumerate(pets):
        print(f"\nPet #{i+1}: {pet.name}")
        print(f"  ID: {pet.id}")
        print(f"  Species: {pet.species}")
        print(f"  Mood: {pet.mood}")
        print(f"  Level: {pet.level}")
        print(f"  Interactions: {pet.interactionCount}")
    
    return pets

def test_api_fixed_pet(email, password):
    """Test the fixed-pet endpoint for consistency"""
    print("\n=== Testing Fixed Pet Endpoint ===")
    
    # First, login to get a session ID
    print(f"\n1. Logging in with email: {email}")
    login_response = requests.post(
        f"{API_BASE_URL}/api/login", 
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        return False
    
    session_id = login_response.json().get("session_id")
    print(f"Login successful! Session ID: {session_id[:8]}...")
    
    # Set up headers with the session ID
    headers = {"session-id": session_id}
    
    # Call fixed-pet endpoint multiple times
    pet_ids = []
    for i in range(3):
        print(f"\n2.{i+1} Requesting fixed pet (attempt {i+1})...")
        response = requests.get(f"{API_BASE_URL}/api/fixed-pet", headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to get fixed pet: {response.status_code} - {response.text}")
            continue
        
        pet_data = response.json()
        pet_id = pet_data.get("id") or pet_data.get("_id")
        pet_ids.append(pet_id)
        
        print(f"Got pet with ID: {pet_id}")
        print(f"Pet name: {pet_data.get('name')}")
        print(f"Mood: {pet_data.get('mood')}")
    
    # Check if all pet IDs are the same
    if len(set(pet_ids)) == 1:
        print("\n✅ SUCCESS: All requests returned the same pet ID!")
        return True
    else:
        print("\n❌ FAILURE: Requests returned different pet IDs:")
        for i, pet_id in enumerate(pet_ids):
            print(f"  Request {i+1}: {pet_id}")
        return False

async def test_interaction_with_pet(pet_id):
    """Test interacting with a pet directly via database functions"""
    print(f"\n=== Testing Direct Interaction with Pet ID: {pet_id} ===")
    
    # Verify pet exists
    pet = await PetDB.get_pet(pet_id)
    if not pet:
        print(f"❌ Pet not found with ID: {pet_id}")
        return False
    
    print(f"✅ Found pet: {pet.name}")
    print(f"  Current mood: {pet.mood}")
    print(f"  Interaction count: {pet.interactionCount}")
    
    # Update mood and interaction count
    await PetDB.update_mood(pet_id, "excited")
    await PetDB.increment_interaction(pet_id)
    
    # Verify updates
    updated_pet = await PetDB.get_pet(pet_id)
    print(f"\nAfter updates:")
    print(f"  New mood: {updated_pet.mood}")
    print(f"  New interaction count: {updated_pet.interactionCount}")
    
    return True

async def main():
    """Main function to test the fixed-pet endpoint"""
    print("\n=== FIXED PET ENDPOINT TEST ===")
    
    # Find a valid user email from the database
    valid_email = await find_valid_user()
    
    if valid_email:
        print(f"\nWill attempt login with email: {valid_email}")
        # First test the API endpoint with password "password" (common test password)
        api_test_success = test_api_fixed_pet(valid_email, "password")
    else:
        print("\nNo valid users found in database.")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main()) 