import sys
from api.routes import active_sessions
from database.database import UserDB
import asyncio

async def add_test_session():
    """Add a test session for debugging"""
    
    # Get all users to find one to use
    print("Looking for a user to create a test session...")
    user_email = input("Enter a user email to create session for: ")
    
    user = await UserDB.get_user_by_email(user_email)
    if not user:
        print(f"Error: No user found with email {user_email}")
        return
        
    # Create a test session
    test_session_id = "test_session_" + user.id
    active_sessions[test_session_id] = str(user.id)
    
    print(f"\nCreated test session:")
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Session ID: {test_session_id}")
    print(f"\nTo test, use this session ID in your frontend localStorage")
    print("In the browser console run:")
    print(f"localStorage.setItem('sessionId', '{test_session_id}'); console.log('Session set!')")
    
    # Display all sessions
    print("\n--- ACTIVE SESSIONS ---")
    print(f"Total active sessions: {len(active_sessions)}")
    for sid, uid in active_sessions.items():
        print(f"Session: {sid} -> User: {uid}")
    print("---------------------\n")

if __name__ == "__main__":
    asyncio.run(add_test_session()) 