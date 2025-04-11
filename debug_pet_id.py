#!/usr/bin/env python3
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId
import pprint

# Load environment variables
load_dotenv()

# MongoDB connection string and database name
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

if not MONGODB_URI or not DB_NAME:
    raise ValueError("MongoDB connection settings are not properly configured in environment variables")

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
pets_collection = db["pets"]

def list_all_pets():
    """List all pets in the database"""
    print("\n=== All Pets in Database ===")
    pets = list(pets_collection.find())
    if not pets:
        print("No pets found in database")
        return
    
    for pet in pets:
        print(f"Pet ID: {pet['_id']} (type: {type(pet['_id'])})")
        print(f"Name: {pet.get('name')}")
        print(f"User ID: {pet.get('userId')}")
        print("-" * 30)

def check_pet_by_id(pet_id_str):
    """Check if a pet exists with the given ID string"""
    print(f"\n=== Checking Pet ID: {pet_id_str} ===")
    
    # Try as raw string
    pet = pets_collection.find_one({"_id": pet_id_str})
    if pet:
        print(f"Found pet using raw string ID: {pet_id_str}")
        pprint.pprint(pet)
        return
    
    # Try as ObjectId
    try:
        obj_id = ObjectId(pet_id_str)
        pet = pets_collection.find_one({"_id": obj_id})
        if pet:
            print(f"Found pet using ObjectId: {obj_id}")
            pprint.pprint(pet)
            return
    except Exception as e:
        print(f"Error converting to ObjectId: {str(e)}")
    
    print(f"No pet found with ID: {pet_id_str}")

def get_pets_by_user(user_id_str):
    """Get all pets for a user"""
    print(f"\n=== Checking Pets for User ID: {user_id_str} ===")
    
    # Try as raw string
    pets = list(pets_collection.find({"userId": user_id_str}))
    if pets:
        print(f"Found {len(pets)} pets for user {user_id_str}")
        for pet in pets:
            print(f"Pet ID: {pet['_id']} (type: {type(pet['_id'])})")
            print(f"Name: {pet.get('name')}")
            print("-" * 30)
        return
    
    # Try as ObjectId
    try:
        obj_id = ObjectId(user_id_str)
        pets = list(pets_collection.find({"userId": obj_id}))
        if pets:
            print(f"Found {len(pets)} pets for user ObjectId {obj_id}")
            for pet in pets:
                print(f"Pet ID: {pet['_id']}")
                print(f"Name: {pet.get('name')}")
                print("-" * 30)
            return
    except Exception as e:
        print(f"Error converting to ObjectId: {str(e)}")
    
    print(f"No pets found for user: {user_id_str}")

if __name__ == "__main__":
    # List all pets
    list_all_pets()
    
    # Get pet ID from user input
    pet_id_to_check = input("\nEnter pet ID to check: ")
    if pet_id_to_check:
        check_pet_by_id(pet_id_to_check)
    
    # Get user ID from user input
    user_id_to_check = input("\nEnter user ID to check: ")
    if user_id_to_check:
        get_pets_by_user(user_id_to_check) 