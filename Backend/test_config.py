import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

# Test API configuration
TEST_API_URL = "http://testserver"

# Test environment variables
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ENVIRONMENT"] = "test" 