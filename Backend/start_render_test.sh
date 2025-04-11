#!/bin/bash

# This script runs the MongoDB connectivity test on Render
# It can be used to diagnose connection issues

# Load environment variables
set -o allexport
source .env
set +o allexport

# Print environment information
echo "====== Environment Information ======"
echo "Running on: $(uname -a)"
echo "PATH: $PATH"
echo "PYTHONPATH: $PYTHONPATH"
echo "SSL_CERT_DIR: $SSL_CERT_DIR"
echo "SSL_CERT_FILE: $SSL_CERT_FILE"
echo "===================================="

# Check OpenSSL version
echo "OpenSSL version:"
openssl version

# Check CA certificates
echo "CA certificate location:"
which -a cert-locate 2>/dev/null || echo "cert-locate not found"

# Set Render environment marker
export IS_RENDER=true

# Run the test script
echo "Running MongoDB connection test..."
python render_test.py

# Exit with the same code as the test script
exit $? 