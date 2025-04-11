import sys
import os
from api.routes import active_sessions

def check_sessions():
    """Print the current active sessions"""
    print("\n--- ACTIVE SESSIONS ---")
    print(f"Total active sessions: {len(active_sessions)}")
    for session_id, user_id in active_sessions.items():
        print(f"Session: {session_id[:8]}... -> User: {user_id}")
    print("---------------------\n")

if __name__ == "__main__":
    check_sessions() 