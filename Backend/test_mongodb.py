import os
import sys
import platform
import ssl
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient, __version__ as pymongo_version
from pymongo.server_api import ServerApi

# Print system information for debugging
print("\n=== System Information ===")
print(f"Platform: {platform.platform()}")
print(f"Python version: {platform.python_version()}")
print(f"SSL version: {ssl.OPENSSL_VERSION}")
print(f"Certifi path: {certifi.where()}")
print(f"Pymongo version: {pymongo_version}")
print("==========================\n")

# Load environment variables
load_dotenv()

# Get MongoDB connection string 
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

if not MONGODB_URI or not DB_NAME:
    print("ERROR: MongoDB settings not found in environment variables")
    sys.exit(1)

print(f"Testing connection to database: {DB_NAME}")
uri_parts = MONGODB_URI.split('@') if MONGODB_URI else []
if len(uri_parts) > 1:
    safe_uri = f"...@{uri_parts[-1]}"
    print(f"Using MongoDB URI: {safe_uri}")

# Test 1: Simple connection
try:
    print("\nTest 1: Attempting simple connection...")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 1: Success!")
except Exception as e:
    print(f"Test 1 ERROR: {type(e).__name__} - {str(e)}")

# Test 2: Using tlsCAFile
try:
    print("\nTest 2: Using tlsCAFile with system CA certificates...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where()
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 2: Success!")
except Exception as e:
    print(f"Test 2 ERROR: {type(e).__name__} - {str(e)}")

# Test 3: Using ServerApi for version compatibility
try:
    print("\nTest 3: Using ServerApi for version compatibility...")
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsCAFile=certifi.where()
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 3: Success!")
except Exception as e:
    print(f"Test 3 ERROR: {type(e).__name__} - {str(e)}")

# Test 4: With relaxed TLS settings
try:
    print("\nTest 4: With relaxed TLS settings...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 4: Success!")
except Exception as e:
    print(f"Test 4 ERROR: {type(e).__name__} - {str(e)}")

# Test 5: Adding connect=False option
try:
    print("\nTest 5: Adding connect=False option...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connect=False,
        tls=True,
        tlsCAFile=certifi.where()
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 5: Success!")
except Exception as e:
    print(f"Test 5 ERROR: {type(e).__name__} - {str(e)}")

# Test 6: Minimal URI connection
try:
    print("\nTest 6: Minimal URI connection (no TLS params)...")
    # Try to connect only using the URI without additional TLS parameters
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 6: Success!")
except Exception as e:
    print(f"Test 6 ERROR: {type(e).__name__} - {str(e)}")

print("\nAll connection tests completed.") 