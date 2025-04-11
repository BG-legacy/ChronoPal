#!/usr/bin/env python3
import requests
import json
import sys

# Base URL for API
API_BASE_URL = 'http://localhost:8000/api'

def register_user(username, email, password):
    """Register a new user"""
    url = f"{API_BASE_URL}/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    print(f"Registering user: {username} with email {email}")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Registration successful!")
        print(f"User: {result['username']}")
        print(f"ID: {result['id']}")
        return result
    else:
        print(f"Registration failed: {response.status_code} - {response.text}")
        return None

def login(email, password):
    """Login to get a session ID"""
    url = f"{API_BASE_URL}/login"
    data = {
        "email": email,
        "password": password
    }
    
    print(f"Logging in as {email}")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Login successful for {result['user']['username']}")
        print(f"Session ID: {result['session_id'][:8]}...")
        return result
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def create_pet(session_id, pet_name):
    """Create a new pet for the user"""
    url = f"{API_BASE_URL}/save-pet"
    headers = {
        "session-id": session_id,
        "Content-Type": "application/json"
    }
    
    data = {
        "name": pet_name,
        "species": "Digital"
    }
    
    print(f"Creating pet: {pet_name}")
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Pet created successfully!")
        print(f"Pet name: {result['name']}")
        print(f"Pet ID: {result.get('id') or result.get('_id')}")
        return result
    else:
        print(f"Pet creation failed: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # Test user details
    username = "testuser"
    email = "test@example.com"
    password = "password123"
    pet_name = "TestPet"
    
    # Register new user
    user = register_user(username, email, password)
    if not user:
        print("Trying to login instead...")
        # Try to login if registration fails (user might already exist)
        login_result = login(email, password)
        if not login_result:
            sys.exit(1)
        session_id = login_result["session_id"]
    else:
        # Login with the newly registered user
        login_result = login(email, password)
        if not login_result:
            sys.exit(1)
        session_id = login_result["session_id"]
    
    # Create a pet for the user
    pet = create_pet(session_id, pet_name)
    if not pet:
        print("Failed to create pet")
        sys.exit(1)
    
    print("\nTest user and pet created successfully!")
    print(f"You can now login with email: {email} and password: {password}")
    print(f"And interact with pet {pet_name} (ID: {pet.get('id') or pet.get('_id')})") 