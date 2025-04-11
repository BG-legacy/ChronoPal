#!/usr/bin/env python
"""
This script tests MongoDB connectivity specifically for Render deployment.
It tries various connection methods and reports the results.
"""

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
print(f"Environment: {'RENDER' if os.environ.get('IS_RENDER') else 'Local'}")
print("==========================\n")

# Load environment variables
load_dotenv()

# Get MongoDB connection string 
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

if not MONGODB_URI or not DB_NAME:
    print("ERROR: MongoDB settings not found in environment variables")
    sys.exit(1)

uri_parts = MONGODB_URI.split('@') if MONGODB_URI else []
if len(uri_parts) > 1:
    safe_uri = f"...@{uri_parts[-1]}"
    print(f"Using MongoDB URI: {safe_uri}")

# Try different connection strategies

# Strategy 1: Simple ServerApi
try:
    print("\nStrategy 1: Using ServerApi...")
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=5000
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    client.close()
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {str(e)}")

# Strategy 2: TLS with CA File
try:
    print("\nStrategy 2: TLS with CA File...")
    client = MongoClient(
        MONGODB_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    client.close()
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {str(e)}")

# Strategy 3: TLS with Allow Invalid Certificates
try:
    print("\nStrategy 3: TLS with Allow Invalid Certificates...")
    client = MongoClient(
        MONGODB_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    client.close()
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {str(e)}")

# Strategy 4: ServerApi with TLS and CA File
try:
    print("\nStrategy 4: ServerApi with TLS and CA File...")
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    client.close()
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {str(e)}")

# Strategy 5: ServerApi with TLS Allow Invalid Certificates
try:
    print("\nStrategy 5: ServerApi with TLS Allow Invalid Certificates...")
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    client.close()
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {str(e)}")

# Strategy 6: URI Only
try:
    print("\nStrategy 6: URI Only (minimal parameters)...")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    server_info = client.server_info()
    print(f"SUCCESS: Connected to MongoDB version: {server_info.get('version')}")
    client.close()
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {str(e)}")

print("\nAll connection tests completed.") 