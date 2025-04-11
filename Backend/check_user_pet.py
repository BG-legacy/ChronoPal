#!/usr/bin/env python
"""
Utility script to check user's pet in the database.
This helps debug issues with pet interactions.
"""

import asyncio
import os
import sys
from database.database import PetDB, UserDB
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# MongoDB connection string and database name
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

if not MONGODB_URI or not DB_NAME:
    print("ERROR: MongoDB connection settings are not properly configured in environment variables")
    sys.exit(1)

async def check_connection():
    """Test the MongoDB connection"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")
        return False

async def get_active_sessions():
    """Get all active session IDs from routes.py module"""
    try:
        from api.routes import active_sessions
        print(f"\n== Active Sessions ({len(active_sessions)}) ==")
        for session_id, user_id in active_sessions.items():
            print(f"Session: {session_id[:8]}... -> User: {user_id}")
        return active_sessions
    except Exception as e:
        print(f"❌ Error getting active sessions: {str(e)}")
        return {}

async def get_user_by_email(email):
    """Get user by email"""
    try:
        user = await UserDB.get_user_by_email(email)
        if user:
            print(f"\n== User: {user.username} ==")
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            return user
        else:
            print(f"❌ No user found with email: {email}")
            return None
    except Exception as e:
        print(f"❌ Error getting user: {str(e)}")
        return None

async def get_pets_for_user(user_id):
    """Get all pets for a user"""
    try:
        pets = await PetDB.get_pets_by_user(user_id)
        print(f"\n== Pets for User {user_id} ({len(pets)}) ==")
        
        if not pets:
            print("No pets found for this user.")
            return []
            
        for i, pet in enumerate(pets):
            print(f"\nPet #{i+1}: {pet.name}")
            print(f"  ID: {pet.id}")
            print(f"  Species: {pet.species}")
            print(f"  Level: {pet.level}")
            print(f"  Mood: {pet.mood}")
            print(f"  Interactions: {pet.interactionCount}")
            
            # Test if the ID is valid and can be found in the database
            direct_pet = await PetDB.get_pet(pet.id)
            if direct_pet:
                print(f"  ✅ Pet can be accessed directly by ID: {pet.id}")
            else:
                print(f"  ❌ Pet CANNOT be accessed directly by ID: {pet.id}")
                
            # Test ObjectId validity
            if ObjectId.is_valid(pet.id):
                print(f"  ✅ ID is valid ObjectId format")
            else:
                print(f"  ❌ ID is NOT a valid ObjectId format")
        
        return pets
    except Exception as e:
        print(f"❌ Error getting pets: {str(e)}")
        return []

async def test_pet_interaction(pet_id, interaction_type="feed"):
    """Test pet interaction"""
    try:
        print(f"\n== Testing {interaction_type} interaction for pet {pet_id} ==")
        
        # First check if pet exists
        pet = await PetDB.get_pet(pet_id)
        if not pet:
            print(f"❌ Pet not found with ID: {pet_id}")
            return False
            
        print(f"✅ Pet found: {pet.name}")
        
        # Test update methods based on interaction type
        if interaction_type == "feed":
            updated_pet = await PetDB.update_last_fed(pet_id)
            if updated_pet:
                print(f"✅ Successfully fed pet")
            else:
                print(f"❌ Failed to feed pet")
        elif interaction_type == "play":
            updated_pet = await PetDB.update_mood(pet_id, "excited")
            if updated_pet:
                print(f"✅ Successfully played with pet")
            else:
                print(f"❌ Failed to play with pet")
        elif interaction_type == "teach":
            updated_pet = await PetDB.add_memory(pet_id, "Test memory from diagnostic tool")
            if updated_pet:
                print(f"✅ Successfully taught pet")
            else:
                print(f"❌ Failed to teach pet")
        
        # Test increment interaction
        updated_pet = await PetDB.increment_interaction(pet_id)
        if updated_pet:
            print(f"✅ Successfully incremented interaction count to {updated_pet.interactionCount}")
            return True
        else:
            print(f"❌ Failed to increment interaction count")
            return False
    except Exception as e:
        print(f"❌ Error testing interaction: {str(e)}")
        return False

async def main():
    """Main function"""
    print("=============================================")
    print("ChronoPal Pet Database Diagnostic Tool")
    print("=============================================")
    
    # Check connection
    if not await check_connection():
        return
    
    # Get active sessions
    sessions = await get_active_sessions()
    
    # Ask for email
    email = input("\nEnter user email (or leave empty to skip): ")
    if email:
        user = await get_user_by_email(email)
        if user:
            pets = await get_pets_for_user(user.id)
            
            if pets:
                # Test interaction
                choice = input("\nWould you like to test a pet interaction? (y/n): ")
                if choice.lower() == 'y':
                    pet_id = input("Enter pet ID: ")
                    interaction = input("Enter interaction type (feed, play, teach): ")
                    await test_pet_interaction(pet_id, interaction)
    
    print("\n=============================================")
    print("Diagnostic complete!")
    print("=============================================")

if __name__ == "__main__":
    asyncio.run(main()) 