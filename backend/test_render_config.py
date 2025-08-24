#!/usr/bin/env python3
"""
Test script to validate Render configuration locally
Run this before deploying to ensure everything is configured correctly
"""

import os
import sys
from pathlib import Path

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔍 Testing environment variables...")
    
    required_vars = ["GOOGLE_API_KEY"]
    optional_vars = ["ENVIRONMENT", "RENDER", "PORT", "CHROMA_PERSIST_DIR", "UPLOAD_DIR", "FAISS_CACHE_DIR"]
    
    # Test required variables
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    # Test optional variables
    print("Environment variables:")
    for var in required_vars + optional_vars:
        value = os.getenv(var, "not set")
        if var == "GOOGLE_API_KEY":
            display_value = f"{value[:8]}..." if len(value) > 8 else "***"
        else:
            display_value = value
        print(f"  {var}: {display_value}")
    
    print("✅ Environment variables test passed!")
    return True

def test_config_import():
    """Test that the config module can be imported and used"""
    print("\n🔍 Testing configuration import...")
    
    try:
        from config import get_config
        config = get_config()
        print("✅ Config import successful!")
        
        # Test storage configuration
        storage_config = config.get_storage_config()
        print(f"  Storage config: {storage_config}")
        
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_storage_setup():
    """Test that storage setup script works"""
    print("\n🔍 Testing storage setup...")
    
    try:
        from setup_storage import setup_storage
        result = setup_storage()
        if result:
            print("✅ Storage setup test passed!")
            return True
        else:
            print("❌ Storage setup test failed!")
            return False
    except Exception as e:
        print(f"❌ Storage setup test failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist and are writable"""
    print("\n🔍 Testing directory structure...")
    
    directories = [
        "./uploads",
        "./chroma_db", 
        "./faiss_cache"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            
            # Test write permission
            test_file = Path(directory) / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            
            print(f"✅ Directory {directory} is writable")
        except Exception as e:
            print(f"❌ Directory {directory} test failed: {e}")
            return False
    
    print("✅ Directory structure test passed!")
    return True

def test_dependencies():
    """Test that all required dependencies can be imported"""
    print("\n🔍 Testing dependencies...")
    
    required_modules = [
        "fastapi",
        "uvicorn", 
        "google.generativeai",
        "langchain",
        "chromadb",
        "PyPDF2",
        "fitz"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            return False
    
    print("✅ Dependencies test passed!")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 IntelliClaim Render Configuration Test")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Configuration Import", test_config_import),
        ("Storage Setup", test_storage_setup),
        ("Directory Structure", test_directory_structure),
        ("Dependencies", test_dependencies)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed!")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your configuration is ready for Render deployment.")
        print("\nNext steps:")
        print("1. Commit your changes to Git")
        print("2. Follow the deployment checklist in RENDER_DEPLOYMENT_CHECKLIST.md")
        print("3. Deploy to Render!")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        print("\nCheck the error messages above and fix any configuration issues.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
