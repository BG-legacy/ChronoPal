#!/usr/bin/env python
"""
Script to directly check if the API server is using our updated code
"""

import os
import sys
import signal
import subprocess
import time
import requests

# Test server configurations
API_HOST = "127.0.0.1"
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"

def check_api_health():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is running")
            print(f"  Version: {data.get('version', 'unknown')}")
            print(f"  Active sessions: {data.get('active_sessions', 'unknown')}")
            return True
        else:
            print(f"✗ API returned non-200 status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to API at {API_URL}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error checking API health: {str(e)}")
        return False

def run_test_server():
    """Start a new test API server"""
    print(f"\n=== Starting Test API Server ===")
    print(f"Host: {API_HOST}")
    print(f"Port: {API_PORT}")
    
    try:
        # Build the command to start the API server
        api_cmd = [
            "uvicorn", 
            "api.main:app", 
            "--host", API_HOST, 
            "--port", str(API_PORT),
            "--reload"  # Enable auto-reload for code changes
        ]
        
        # Start the server in a new process
        server_process = subprocess.Popen(
            api_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        print(f"Server process started with PID: {server_process.pid}")
        print(f"Waiting for server to start...")
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Check if server is running
        if check_api_health():
            print(f"✓ Test server is up and running")
            return server_process
        else:
            print(f"✗ Failed to start test server")
            server_process.terminate()
            print("Server process terminated")
            return None
    except Exception as e:
        print(f"✗ Error starting test server: {str(e)}")
        return None

def stop_test_server(process):
    """Stop the test API server"""
    if process:
        print(f"\n=== Stopping Test API Server ===")
        process.terminate()
        process.wait(timeout=5)
        print(f"Server process terminated")

def check_frontend_api_url():
    """Check what API URL the frontend is using"""
    try:
        # Try to find apiService.ts file
        frontend_dir = "../frontend/src/services"
        apiservice_path = os.path.join(frontend_dir, "apiService.ts")
        
        if os.path.exists(apiservice_path):
            with open(apiservice_path, 'r') as f:
                content = f.read()
                
            # Look for API_BASE_URL
            import re
            api_url_match = re.search(r'API_BASE_URL\s*=\s*[\'"]([^\'"]+)[\'"]', content)
            
            if api_url_match:
                frontend_api_url = api_url_match.group(1)
                print(f"\n=== Frontend API URL Check ===")
                print(f"Frontend is using API URL: {frontend_api_url}")
                
                if frontend_api_url != API_URL:
                    print(f"⚠️ WARNING: Frontend API URL ({frontend_api_url}) doesn't match test server URL ({API_URL})")
                    print(f"This could explain why frontend can't connect to the backend.")
                else:
                    print(f"✓ Frontend API URL matches test server URL")
                    
                return frontend_api_url
            else:
                print(f"✗ Couldn't find API_BASE_URL in apiService.ts")
                return None
        else:
            print(f"✗ Couldn't find apiService.ts at {apiservice_path}")
            return None
    except Exception as e:
        print(f"✗ Error checking frontend API URL: {str(e)}")
        return None

def main():
    """Main function to test the API server"""
    print("\n=== API SERVER DEBUG ===")
    
    # First, check if the API server is already running
    api_running = check_api_health()
    
    if not api_running:
        print("\nNo API server currently running. Starting a new one...")
        server_process = run_test_server()
    else:
        print("\nAPI server is already running.")
        server_process = None
    
    # Check what API URL the frontend is using
    frontend_api_url = check_frontend_api_url()
    
    # If we started a server, stop it
    if server_process:
        input("\nPress Enter to stop the test server...")
        stop_test_server(server_process)
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    main() 