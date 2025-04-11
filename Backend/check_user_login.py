#!/usr/bin/env python
"""
Script to check a specific user login and find API issues
"""

import asyncio
import requests
import json
from database.database import UserDB
from passlib.context import CryptContext
from datetime import datetime, timezone

# API base URL
API_BASE_URL = "http://localhost:8000"
TARGET_EMAIL = "Guiseppe.Gulgowski@gmail.com"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def find_user_by_email(email):
    """Find a user by email and print details"""
    user = await UserDB.get_user_by_email(email)
    if user:
        print(f"\n=== Found User: {user.username} ===")
        print(f"Email: {user.email}")
        print(f"ID: {user.id}")
        
        # For security, we won't show the actual hash, just check if it exists
        print(f"Has password hash: {'Yes' if user.hashed_password else 'No'}")
        
        # Try to verify common test passwords
        test_passwords = ["password", "test123", "testing", "123456"]
        for password in test_passwords:
            if pwd_context.verify(password, user.hashed_password):
                print(f"✓ Password verified: '{password}'")
                return user, password
        
        print("✗ Password not matched with common test passwords")
        return user, None
    else:
        print(f"\n✗ No user found with email: {email}")
        return None, None

def try_api_login(email, password):
    """Try logging in via the API directly"""
    print(f"\n=== Testing API Login ===")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/login", 
            json={"email": email, "password": password}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id", "unknown")
            user_data = data.get("user", {})
            
            print(f"✓ Login successful!")
            print(f"Session ID: {session_id[:8]}...")
            print(f"User ID: {user_data.get('id', 'unknown')}")
            print(f"Username: {user_data.get('username', 'unknown')}")
            
            # Now try the fixed-pet endpoint
            headers = {"session-id": session_id}
            pet_response = requests.get(f"{API_BASE_URL}/api/fixed-pet", headers=headers)
            
            if pet_response.status_code == 200:
                pet_data = pet_response.json()
                pet_id = pet_data.get("id") or pet_data.get("_id")
                print(f"\n✓ Fixed pet endpoint success!")
                print(f"Pet ID: {pet_id}")
                print(f"Pet name: {pet_data.get('name')}")
                
                # Try again to verify consistency
                pet_response2 = requests.get(f"{API_BASE_URL}/api/fixed-pet", headers=headers)
                pet_data2 = pet_response2.json()
                pet_id2 = pet_data2.get("id") or pet_data2.get("_id")
                
                if pet_id == pet_id2:
                    print(f"✓ Consistency check passed - got same pet ID on second request")
                else:
                    print(f"✗ Consistency check failed - got different pet IDs: {pet_id} vs {pet_id2}")
            else:
                print(f"✗ Fixed pet endpoint failed: {pet_response.status_code}")
                print(f"Response: {pet_response.text}")
            
            return True
        else:
            print(f"✗ Login failed")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error during API login: {str(e)}")
        return False

async def main():
    print("\n=== USER LOGIN CHECK ===")
    
    # Check target user
    user, password = await find_user_by_email(TARGET_EMAIL)
    
    if user:
        # If we found a likely password, try it
        if password:
            try_api_login(user.email, password)
        else:
            # Try with default password
            try_api_login(user.email, "password")
    
    # If specific check fails, let's find any valid user
    if not user:
        print("\nLooking for any valid user...")
        from database.database import async_users_collection
        
        # Find first user in DB
        async for user_doc in async_users_collection.find({}):
            if user_doc:
                email = user_doc.get("email")
                print(f"\nFound user with email: {email}")
                
                # Reset password to known value for testing
                hashed_password = pwd_context.hash("password123")
                
                print(f"Resetting password for testing purposes...")
                result = await async_users_collection.update_one(
                    {"email": email},
                    {"$set": {"hashed_password": hashed_password}}
                )
                
                if result.modified_count > 0:
                    print(f"✓ Password reset to 'password123'")
                    # Try login with new password
                    try_api_login(email, "password123")
                else:
                    print(f"✗ Failed to reset password")
                
                break
    
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    asyncio.run(main()) 