#!/usr/bin/env python3
"""
Quick environment check for IntelliClaim demo
"""

import os
import sys

print("=" * 50)
print("IntelliClaim Environment Check")
print("=" * 50)
print()

# Check API keys
aimlapi_key = os.getenv("AIMLAPI_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

print("API Keys:")
print(f"  AIMLAPI_KEY: {'✅ Set' if aimlapi_key else '❌ Not set'}")
print(f"  GOOGLE_API_KEY: {'✅ Set' if google_key else '❌ Not set'}")
print()

if not aimlapi_key or not google_key:
    print("⚠️  WARNING: API keys are missing!")
    print()
    print("Please create a .env file in the backend directory with:")
    print("  AIMLAPI_KEY=your_aimlapi_key_here")
    print("  GOOGLE_API_KEY=your_google_api_key_here")
    print("  ENVIRONMENT=development")
    print()
    sys.exit(1)

# Check required directories
print("Directories:")
for dir_name in ["chroma_db", "uploads", "faiss_cache"]:
    exists = os.path.exists(dir_name)
    print(f"  {dir_name}/: {'✅ Exists' if exists else '⚠️  Missing (will be created)'}")

print()
print("✅ Environment looks good!")
print()
print("To start the server, run:")
print("  python chatgpt_app.py")
print()

