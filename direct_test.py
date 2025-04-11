#!/usr/bin/env python3
import requests
import json
import sys
from pprint import pprint

# Setup
base_url = "http://localhost:8000/api"
email = "testuser2@example.com"
password = "password123"

# Login
def login():
    print("Logging in...")
    response = requests.post(f"{base_url}/login", json={
        "email": email,
        "password": password
    })
    
    if response.status_code != 200:
        print(f"Login failed with status {response.status_code}")
        print(response.text)
        sys.exit(1)
        
    data = response.json()
    session_id = data["session_id"]
    print(f"Login successful, session ID: {session_id[:8]}...")
    return session_id

# Get the user's pet
def get_pet(session_id):
    print("Getting pet...")
    headers = {"session-id": session_id}
    
    # Try to get the most reliable pet ID by checking both endpoints
    print("\nChecking user-pet endpoint (primary):")
    user_pet_response = requests.get(f"{base_url}/user-pet", headers=headers)
    
    if user_pet_response.status_code == 200:
        user_pet = user_pet_response.json()
        print("User-pet data:")
        pprint(user_pet)
        
        # Get ID from user-pet response
        if user_pet.get('id') is None and user_pet.get('_id'):
            user_pet['id'] = user_pet['_id']
            print(f"Fixed missing id using _id: {user_pet['id']}")
        
        pet_id = user_pet.get('id')
        print(f"Using pet ID from user-pet: {pet_id}")
        return user_pet
    else:
        print(f"Failed to get pet from user-pet endpoint: {user_pet_response.status_code}")
        
    # Fallback to fixed-pet if user-pet fails
    print("\nFalling back to fixed-pet endpoint:")
    fixed_pet_response = requests.get(f"{base_url}/fixed-pet", headers=headers)
    
    if fixed_pet_response.status_code != 200:
        print(f"Failed to get pet with status {fixed_pet_response.status_code}")
        print(fixed_pet_response.text)
        sys.exit(1)
        
    data = fixed_pet_response.json()
    print("Fixed-pet data:")
    pprint(data)
    
    # Fix missing ID if needed
    if data.get('id') is None and data.get('_id'):
        data['id'] = data['_id']
        print(f"Fixed missing id using _id: {data['id']}")
    
    pet_id = data.get('id')
    if not pet_id:
        print("ERROR: Pet has no ID!")
        sys.exit(1)
        
    print(f"Using pet ID from fixed-pet: {pet_id}")
    return data

# Test all endpoints individually
def test_direct_endpoints(session_id, pet_id):
    headers = {"session-id": session_id}
    
    # Test each endpoint individually with different methods
    
    # 1. Try query parameters
    print("\nTesting with query parameters:")
    
    # Feed
    print("Testing feed endpoint with query parameters...")
    feed_response = requests.post(
        f"{base_url}/feed-pet?pet_id={pet_id}",
        headers=headers
    )
    print(f"Feed response: {feed_response.status_code} - {feed_response.text[:100]}")
    
    # Play
    print("Testing play endpoint with query parameters...")
    play_response = requests.post(
        f"{base_url}/play-with-pet?pet_id={pet_id}",
        headers=headers
    )
    print(f"Play response: {play_response.status_code} - {play_response.text[:100]}")
    
    # Teach
    print("Testing teach endpoint with query parameters...")
    teach_response = requests.post(
        f"{base_url}/teach-pet?pet_id={pet_id}&message=Test+lesson",
        headers=headers
    )
    print(f"Teach response: {teach_response.status_code} - {teach_response.text[:100]}")
    
    # 2. Try form data
    print("\nTesting with form data:")
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    
    # Feed
    print("Testing feed endpoint with form data...")
    feed_response = requests.post(
        f"{base_url}/feed-pet",
        headers=headers,
        data={"pet_id": pet_id}
    )
    print(f"Feed response: {feed_response.status_code} - {feed_response.text[:100]}")
    
    # Play
    print("Testing play endpoint with form data...")
    play_response = requests.post(
        f"{base_url}/play-with-pet",
        headers=headers,
        data={"pet_id": pet_id}
    )
    print(f"Play response: {play_response.status_code} - {play_response.text[:100]}")
    
    # Teach
    print("Testing teach endpoint with form data...")
    teach_response = requests.post(
        f"{base_url}/teach-pet",
        headers=headers,
        data={"pet_id": pet_id, "message": "Test lesson"}
    )
    print(f"Teach response: {teach_response.status_code} - {teach_response.text[:100]}")
    
    # 3. Try JSON data
    print("\nTesting with JSON data:")
    headers["Content-Type"] = "application/json"
    
    # Feed
    print("Testing feed endpoint with JSON data...")
    feed_response = requests.post(
        f"{base_url}/feed-pet",
        headers=headers,
        json={"pet_id": pet_id}
    )
    print(f"Feed response: {feed_response.status_code} - {feed_response.text[:100]}")
    
    # Play
    print("Testing play endpoint with JSON data...")
    play_response = requests.post(
        f"{base_url}/play-with-pet",
        headers=headers,
        json={"pet_id": pet_id}
    )
    print(f"Play response: {play_response.status_code} - {play_response.text[:100]}")
    
    # Teach
    print("Testing teach endpoint with JSON data...")
    teach_response = requests.post(
        f"{base_url}/teach-pet",
        headers=headers,
        json={"pet_id": pet_id, "message": "Test lesson"}
    )
    print(f"Teach response: {teach_response.status_code} - {teach_response.text[:100]}")

if __name__ == "__main__":
    # Login
    session_id = login()
    
    # Get pet
    pet = get_pet(session_id)
    pet_id = pet.get('id')
    
    # Test endpoints
    test_direct_endpoints(session_id, pet_id) 