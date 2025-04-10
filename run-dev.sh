#!/bin/bash

# Start the backend server
cd Backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start the frontend development server
cd ../frontend
npm start &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap SIGINT and SIGTERM signals and call cleanup
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 