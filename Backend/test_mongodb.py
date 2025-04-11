import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

# Load environment variables
load_dotenv()

# Get MongoDB connection string 
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

if not MONGODB_URI or not DB_NAME:
    print("ERROR: MongoDB settings not found in environment variables")
    sys.exit(1)

print(f"Testing connection to database: {DB_NAME}")
print(f"MongoDB URI (first 20 chars): {MONGODB_URI[:20]}...")

try:
    # Try to connect with minimal parameters first
    print("\nAttempting simple connection...")
    client = MongoClient(MONGODB_URI)
    
    # Test the connection
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    
    # Check if the database exists
    db = client[DB_NAME]
    collections = db.list_collection_names()
    print(f"Collections in database: {collections}")
    
    # Check if the users collection exists and count documents
    if "users" in collections:
        users_count = db.users.count_documents({})
        print(f"Number of users in database: {users_count}")
    else:
        print("WARNING: 'users' collection not found")
        
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {str(e)}")
    print("\nPossible solutions:")
    print("1. Check if the MongoDB URI is correct")
    print("2. Ensure your IP is in the MongoDB Atlas whitelist")
    print("3. Check network connectivity")
    print("4. Verify database credentials")
    sys.exit(1)
    
print("\nConnection test completed successfully!") 