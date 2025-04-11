#!/usr/bin/env python3
import requests
import json
import sys
from getpass import getpass

# Base URL for API
API_BASE_URL = 'http://localhost:8000/api'

def login(email, password):
    """Login to get a session ID"""
    url = f"{API_BASE_URL}/login"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Login successful for {result['user']['username']}")
        return result
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_user_pet(session_id):
    """Get the current user's pet"""
    url = f"{API_BASE_URL}/user-pet"
    headers = {
        "session-id": session_id
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        pet = response.json()
        print(f"Found pet: {pet.get('name')} (ID: {pet.get('id') or pet.get('_id')})")
        return pet
    else:
        print(f"Failed to get pet: {response.status_code} - {response.text}")
        return None

def test_interaction(session_id, pet_id, interaction_type, message=None):
    """Test the update-interaction endpoint"""
    url = f"{API_BASE_URL}/update-interaction"
    headers = {
        "session-id": session_id,
        "Content-Type": "application/json"
    }
    
    data = {
        "pet_id": pet_id,
        "interaction_type": interaction_type
    }
    
    if message:
        data["message"] = message
    
    print(f"\nTesting interaction with data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Interaction successful!")
        print(f"Updated pet: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Interaction failed: {response.text}")
        return None

if __name__ == "__main__":
    email = input("Enter email: ")
    password = getpass("Enter password: ")
    
    # Login to get session ID
    login_result = login(email, password)
    if not login_result:
        sys.exit(1)
    
    session_id = login_result["session_id"]
    
    # Get user's pet
    pet = get_user_pet(session_id)
    if not pet:
        sys.exit(1)
    
    # Get pet ID - try to get the most reliable one
    pet_id = pet.get("id") or pet.get("_id")
    if not pet_id:
        print("Error: Pet has no ID!")
        sys.exit(1)
    
    # Test interactions
    interactions = [
        {"type": "feed", "message": None},
        {"type": "play", "message": None},
        {"type": "teach", "message": "This is a test memory"}
    ]
    
    for interaction in interactions:
        test_interaction(session_id, pet_id, interaction["type"], interaction["message"]) 