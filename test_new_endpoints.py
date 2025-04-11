#!/usr/bin/env python3
import requests
import json
import time
import sys
from pprint import pprint

# Setup API URL
base_url = "http://localhost:8000/api"

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

# Helper function to login
def login(email, password):
    print_header("LOGGING IN")
    
    login_url = f"{base_url}/login"
    login_data = {
        "email": email,
        "password": password
    }
    
    print_info(f"Attempting login with {email}...")
    
    try:
        response = requests.post(login_url, json=login_data)
        response.raise_for_status()
        
        session_id = response.json().get("session_id")
        user = response.json().get("user")
        
        if session_id:
            print_success(f"Login successful! Session ID: {session_id[:8]}...")
            return session_id, user
        else:
            print_error("Login failed: No session ID returned")
            return None, None
    except requests.exceptions.RequestException as e:
        print_error(f"Login failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print_error(f"Response: {e.response.text}")
        return None, None

# Get the user's pet
def get_pet(session_id):
    print_header("GETTING PET")
    
    headers = {"session-id": session_id}
    pet_url = f"{base_url}/fixed-pet"
    
    try:
        response = requests.get(pet_url, headers=headers)
        response.raise_for_status()
        
        pet = response.json()
        
        # Handle case where id is None but _id exists
        if pet.get('id') is None and pet.get('_id'):
            pet['id'] = pet['_id']
            print_info(f"Fixed missing id using _id: {pet['id']}")
        
        # If still no id, we need to extract it from somewhere
        if pet.get('id') is None:
            print_error("Pet has no ID!")
            if '_id' in pet:
                pet['id'] = pet['_id']
                print_info(f"Set id from _id: {pet['id']}")
        
        print_success(f"Got pet: {pet.get('name')} (ID: {pet.get('id')})")
        return pet
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get pet: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print_error(f"Response: {e.response.text}")
        return None

# Test feed endpoint
def test_feed_pet(session_id, pet_id):
    print_header("TESTING FEED ENDPOINT")
    
    headers = {
        "session-id": session_id,
        "Content-Type": "application/json"
    }
    feed_url = f"{base_url}/feed-pet"
    
    try:
        data = {"pet_id": pet_id}
        print_info(f"Feeding pet with ID: {pet_id}")
        
        response = requests.post(feed_url, headers=headers, json=data)
        response.raise_for_status()
        
        updated_pet = response.json()
        print_success("Feed action successful!")
        print_info(f"Updated pet mood: {updated_pet.get('mood')}")
        print_info(f"Last fed: {updated_pet.get('lastFed')}")
        print_info(f"Interaction count: {updated_pet.get('interactionCount')}")
        return updated_pet
    except requests.exceptions.RequestException as e:
        print_error(f"Feed pet failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print_error(f"Response: {e.response.text}")
        return None

# Test play endpoint
def test_play_with_pet(session_id, pet_id):
    print_header("TESTING PLAY ENDPOINT")
    
    headers = {
        "session-id": session_id,
        "Content-Type": "application/json"
    }
    play_url = f"{base_url}/play-with-pet"
    
    try:
        data = {"pet_id": pet_id}
        print_info(f"Playing with pet ID: {pet_id}")
        
        response = requests.post(play_url, headers=headers, json=data)
        response.raise_for_status()
        
        updated_pet = response.json()
        print_success("Play action successful!")
        print_info(f"Updated pet mood: {updated_pet.get('mood')}")
        print_info(f"Interaction count: {updated_pet.get('interactionCount')}")
        return updated_pet
    except requests.exceptions.RequestException as e:
        print_error(f"Play with pet failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print_error(f"Response: {e.response.text}")
        return None

# Test teach endpoint
def test_teach_pet(session_id, pet_id):
    print_header("TESTING TEACH ENDPOINT")
    
    headers = {
        "session-id": session_id,
        "Content-Type": "application/json"
    }
    teach_url = f"{base_url}/teach-pet"
    
    try:
        lesson = "How to dance the robot!"
        data = {
            "pet_id": pet_id,
            "message": lesson
        }
        print_info(f"Teaching pet ID: {pet_id} - Lesson: '{lesson}'")
        
        response = requests.post(teach_url, headers=headers, json=data)
        response.raise_for_status()
        
        updated_pet = response.json()
        print_success("Teach action successful!")
        print_info(f"Updated pet level: {updated_pet.get('level')}")
        print_info(f"Interaction count: {updated_pet.get('interactionCount')}")
        
        # Check if the memory was added
        memory_log = updated_pet.get('memoryLog', [])
        if memory_log:
            print_info(f"Last memory: {memory_log[-1]}")
        
        return updated_pet
    except requests.exceptions.RequestException as e:
        print_error(f"Teach pet failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print_error(f"Response: {e.response.text}")
        return None

def main():
    # Use hardcoded test credentials
    email = "testuser2@example.com"
    password = "password123"
    
    print_info(f"Using test account: {email}")
    
    # Login
    session_id, user = login(email, password)
    if not session_id:
        print_error("Cannot proceed without logging in")
        sys.exit(1)
    
    # Get pet
    pet = get_pet(session_id)
    if not pet:
        print_error("Cannot proceed without a pet")
        sys.exit(1)
    
    pet_id = pet.get('id')
    
    # Test feed endpoint
    feed_result = test_feed_pet(session_id, pet_id)
    time.sleep(1)  # Wait a bit between requests
    
    # Test play endpoint
    play_result = test_play_with_pet(session_id, pet_id)
    time.sleep(1)  # Wait a bit between requests
    
    # Test teach endpoint
    teach_result = test_teach_pet(session_id, pet_id)
    
    print_header("ALL TESTS COMPLETED")
    
    if feed_result and play_result and teach_result:
        print_success("All endpoints tested successfully!")
    else:
        print_error("Some tests failed")

if __name__ == "__main__":
    main() 