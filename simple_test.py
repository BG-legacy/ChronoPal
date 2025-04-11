#!/usr/bin/env python3
import requests
import json
import sys

# Base URL
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "testuser2@example.com"
TEST_PASSWORD = "password123"

def main():
    # Step 1: Login
    print("Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        sys.exit(1)

    login_data = login_response.json()
    session_id = login_data["session_id"]
    print(f"Login successful - Session ID: {session_id[:8]}...")
    
    # Step 2: Get pet from user-pet endpoint
    headers = {"session-id": session_id}
    print("\nFetching pet from user-pet endpoint...")
    pet_response = requests.get(
        f"{BASE_URL}/user-pet",
        headers=headers
    )
    
    if pet_response.status_code != 200:
        print(f"Failed to get pet: {pet_response.status_code}")
        print(pet_response.text)
        sys.exit(1)
    
    pet_data = pet_response.json()
    
    # Handle MongoDB _id vs id field
    if "_id" in pet_data and not pet_data.get("id"):
        pet_data["id"] = pet_data["_id"]
    
    pet_id = pet_data.get("id")
    print(f"Found pet - ID: {pet_id}, Name: {pet_data.get('name')}")
    
    # Step 3: Test the feed-pet-by-user endpoint
    print("\nTesting feed-pet-by-user endpoint...")
    headers["Content-Type"] = "application/json"
    
    feed_response = requests.post(
        f"{BASE_URL}/feed-pet-by-user",
        headers=headers
    )
    
    # Print the full response
    print(f"\nResponse status: {feed_response.status_code}")
    print(f"Response body: {feed_response.text[:200]}")
    
    # Check if the call was successful
    if feed_response.status_code == 200:
        print("\nFeed request SUCCESSFUL! 🎉")
        
        # Test play endpoint
        print("\nTesting play-with-pet-by-user endpoint...")
        play_response = requests.post(
            f"{BASE_URL}/play-with-pet-by-user",
            headers=headers
        )
        print(f"Play response status: {play_response.status_code}")
        
        if play_response.status_code == 200:
            print("Play request SUCCESSFUL! 🎉")
        else:
            print("Play request FAILED! 😞")
            
        # Test teach endpoint
        print("\nTesting teach-pet-by-user endpoint...")
        teach_response = requests.post(
            f"{BASE_URL}/teach-pet-by-user",
            headers=headers,
            json={"message": "How to be awesome!"}
        )
        print(f"Teach response status: {teach_response.status_code}")
        
        if teach_response.status_code == 200:
            print("Teach request SUCCESSFUL! 🎉")
        else:
            print("Teach request FAILED! 😞")
    else:
        print("\nFeed request FAILED! 😞")
    
if __name__ == "__main__":
    main() 