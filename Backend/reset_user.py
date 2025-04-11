#!/usr/bin/env python
"""
Script to reset a user password and test the fixed-pet API
"""

import asyncio
import os
import sys
import json
import requests
from bson import ObjectId
from database.database import async_users_collection, async_pets_collection
from passlib.context import CryptContext

# Configuration
API_BASE_URL = "http://localhost:8000"
TARGET_EMAIL = "Guiseppe.Gulgowski@gmail.com"  # Email from the logs
NEW_PASSWORD = "chronopal123"  # Simple password for testing

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_user_password():
    """Reset the password for a user"""
    print(f"\n=== Resetting password for {TARGET_EMAIL} ===")
    
    # Find the user
    user = await async_users_collection.find_one({"email": TARGET_EMAIL})
    
    if not user:
        print(f"✗ User not found with email: {TARGET_EMAIL}")
        return None
    
    # Get the user's ID
    user_id = str(user.get("_id"))
    username = user.get("username")
    
    print(f"Found user: {username} (ID: {user_id})")
    
    # Hash new password
    hashed_password = pwd_context.hash(NEW_PASSWORD)
    
    # Update password
    result = await async_users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    if result.modified_count == 0:
        print(f"✗ Failed to update password")
        return None
    
    print(f"✓ Password reset successfully to: {NEW_PASSWORD}")
    
    # Return user info
    return {
        "id": user_id,
        "email": TARGET_EMAIL,
        "username": username
    }

async def list_user_pets(user_id):
    """List all pets for a user"""
    print(f"\n=== Listing pets for user {user_id} ===")
    
    pets = []
    async for pet in async_pets_collection.find({"userId": user_id}):
        pet_id = str(pet.get("_id"))
        name = pet.get("name")
        species = pet.get("species")
        
        print(f"Pet: {name} (ID: {pet_id})")
        pets.append({
            "id": pet_id,
            "name": name,
            "species": species
        })
    
    if not pets:
        print("✗ No pets found for this user")
    else:
        print(f"✓ Found {len(pets)} pets")
    
    return pets

def test_api_login():
    """Test logging in via API"""
    print(f"\n=== Testing API Login ===")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/login",
            json={"email": TARGET_EMAIL, "password": NEW_PASSWORD}
        )
        
        if response.status_code != 200:
            print(f"✗ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        session_id = data.get("session_id")
        
        print(f"✓ Login successful!")
        print(f"Session ID: {session_id[:8]}...")
        
        return session_id
    except Exception as e:
        print(f"✗ Error during login: {str(e)}")
        return None

def test_fixed_pet_endpoint(session_id):
    """Test the fixed-pet endpoint with the session ID"""
    print(f"\n=== Testing Fixed Pet Endpoint ===")
    
    if not session_id:
        print("✗ No session ID provided")
        return False
    
    try:
        headers = {"session-id": session_id}
        
        # Make multiple requests to check consistency
        pet_ids = []
        
        for i in range(3):
            response = requests.get(f"{API_BASE_URL}/api/fixed-pet", headers=headers)
            
            if response.status_code != 200:
                print(f"✗ Request {i+1} failed: {response.status_code}")
                print(f"Response: {response.text}")
                continue
            
            pet_data = response.json()
            pet_id = pet_data.get("id") or pet_data.get("_id")
            pet_ids.append(pet_id)
            
            print(f"Request {i+1} - Pet ID: {pet_id}")
        
        # Check for consistency
        if len(set(pet_ids)) == 1 and pet_ids:
            print(f"✓ All requests returned the same pet ID: {pet_ids[0]}")
            
            # Test interaction endpoint
            try_interaction(session_id, pet_ids[0])
            return True
        elif pet_ids:
            print(f"✗ Inconsistent pet IDs returned: {pet_ids}")
            return False
        else:
            print("✗ No valid pet IDs returned")
            return False
    except Exception as e:
        print(f"✗ Error during fixed pet test: {str(e)}")
        return False

def try_interaction(session_id, pet_id):
    """Try to perform an interaction with the pet"""
    print(f"\n=== Testing Pet Interaction ===")
    
    try:
        headers = {"session-id": session_id}
        payload = {
            "pet_id": pet_id,
            "interaction_type": "feed"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/update-interaction",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"✗ Interaction failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print(f"✓ Interaction successful!")
        return True
    except Exception as e:
        print(f"✗ Error during interaction: {str(e)}")
        return False

async def main():
    """Main function to reset a user and test the API"""
    print("\n=== USER RESET AND API TEST ===")
    
    # Reset the user password
    user = await reset_user_password()
    if not user:
        print("Cannot proceed without valid user")
        return
    
    # List the user's pets
    pets = await list_user_pets(user["id"])
    
    # Test API login
    session_id = test_api_login()
    
    # Test fixed pet endpoint
    if session_id:
        test_fixed_pet_endpoint(session_id)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main()) 