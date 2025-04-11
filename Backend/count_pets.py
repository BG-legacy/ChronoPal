#!/usr/bin/env python
"""
Script to count pets in the database and output debugging info
"""

import asyncio
from database.database import PetDB, async_pets_collection
from bson import ObjectId

async def count_pets():
    """Count total pets and print debug info"""
    total = 0
    user_pets = {}
    
    print("\n=== PET DATABASE ANALYSIS ===")
    
    async for pet in async_pets_collection.find({}):
        total += 1
        user_id = pet.get('userId', 'unknown')
        
        if user_id not in user_pets:
            user_pets[user_id] = []
        
        pet_id = str(pet.get('_id', 'unknown'))
        user_pets[user_id].append(pet_id)
    
    print(f'Total pets in database: {total}')
    print(f'Total unique users with pets: {len(user_pets)}')
    print("\n=== USERS WITH MULTIPLE PETS ===")
    
    for user_id, pet_ids in user_pets.items():
        if len(pet_ids) > 1:
            print(f'User {user_id} has {len(pet_ids)} pets:')
            for pet_id in pet_ids:
                print(f'  - {pet_id}')
    
    # Create index on userId for faster queries
    await async_pets_collection.create_index([('userId', 1)])
    print("\nCreated index on userId field")

if __name__ == "__main__":
    asyncio.run(count_pets()) 