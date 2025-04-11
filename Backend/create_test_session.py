#!/usr/bin/env python
"""
Utility script to create a test session for a user.
This bypasses normal login and creates a session directly.
"""

import asyncio
import os
from database.database import UserDB
from api.routes import active_sessions
from dotenv import load_dotenv
import json
import sys
import aiohttp

# Load environment variables
load_dotenv()

async def create_test_session(email):
    """Create a test session for a user"""
    try:
        # Get user by email
        user = await UserDB.get_user_by_email(email)
        if not user:
            print(f"Error: No user found with email {email}")
            return None
            
        print(f"Found user: {user.username} (ID: {user.id})")
        
        # Create a new session
        session_id = os.urandom(16).hex()
        active_sessions[session_id] = str(user.id)
        
        print(f"Created session ID: {session_id}")
        print(f"To use this session ID in curl requests:")
        print(f'  curl -X GET http://localhost:8000/api/user-pet -H "session-id: {session_id}"')
        print(f'  curl -X POST http://localhost:8000/api/update-interaction -H "Content-Type: application/json" -H "session-id: {session_id}" -d \'{{"pet_id": "PET_ID_HERE", "interaction_type": "feed"}}\'')
        
        # Write session ID to file for easy access
        with open(os.path.expanduser("~/.chronopal_session_id"), "w") as f:
            f.write(session_id)
        print(f"Session ID saved to ~/.chronopal_session_id")
        
        # Verify session exists in active_sessions
        if session_id in active_sessions:
            print(f"✅ Session verified in active_sessions with user: {active_sessions[session_id]}")
            
            # Try a simple call to verify session actually works
            async with aiohttp.ClientSession() as session:
                headers = {"session-id": session_id}
                async with session.get("http://localhost:8000/api/health", headers=headers) as response:
                    health_data = await response.json()
                    print(f"API Health: {health_data}")
                    print(f"Active sessions reported by API: {health_data.get('active_sessions', 0)}")
                
                # Try to get user's pet
                print("\nTesting user-pet API call...")
                async with session.get("http://localhost:8000/api/user-pet", headers=headers) as response:
                    if response.status == 200:
                        pet_data = await response.json()
                        print(f"✅ Successfully retrieved pet: {pet_data.get('name')} (ID: {pet_data.get('id')})")
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to get pet: {response.status} - {error_text}")
                        print("This suggests sessions aren't persisting between requests!")
        else:
            print("❌ Session was not added to active_sessions!")
            print("Current active sessions:", active_sessions)
            
        return session_id
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return None

async def main():
    """Main function"""
    print("=============================================")
    print("ChronoPal Test Session Generator")
    print("=============================================")
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter user email: ")
        
    if not email:
        print("Error: Email is required")
        return
        
    # Create test session
    session_id = await create_test_session(email)
    
    if session_id:
        print("\nSession created successfully!")
    else:
        print("\nFailed to create session")

if __name__ == "__main__":
    asyncio.run(main()) 