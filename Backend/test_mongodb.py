import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys
import ssl

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
    import certifi
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

# Test 3: Fully configured connection
try:
    print("\nTest 3: Using explicit SSL context with CERT_REQUIRED...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        ssl=True,
        ssl_cert_reqs=ssl.CERT_REQUIRED,
        ssl_ca_certs=certifi.where()
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 3: Success!")
except Exception as e:
    print(f"Test 3 ERROR: {type(e).__name__} - {str(e)}")

# Test 4: No SSL verification
try:
    print("\nTest 4: Using CERT_NONE (no verification)...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        ssl=True,
        ssl_cert_reqs=ssl.CERT_NONE
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 4: Success!")
except Exception as e:
    print(f"Test 4 ERROR: {type(e).__name__} - {str(e)}")

# Test 5: Newer style TLS parameters
try:
    print("\nTest 5: Using newer style TLS parameters...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
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

# Test 6: Just TLS=True
try:
    print("\nTest 6: Just TLS=True, no additional parameters...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        tls=True
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    print(f"Collections in database: {client[DB_NAME].list_collection_names()}")
    client.close()
    print("Test 6: Success!")
except Exception as e:
    print(f"Test 6 ERROR: {type(e).__name__} - {str(e)}")

print("\nAll connection tests completed.") 