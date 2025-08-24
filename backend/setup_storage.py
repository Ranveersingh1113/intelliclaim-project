#!/usr/bin/env python3
"""
Storage setup script for IntelliClaim Render deployment
Creates necessary directories and validates storage configuration
"""

import os
import sys
from pathlib import Path
from config import get_config

def setup_storage():
    """Setup storage directories for Render deployment"""
    config = get_config()
    
    # Get storage paths from configuration
    storage_config = config.get_storage_config()
    
    directories = [
        storage_config["upload_directory"],
        storage_config["chroma_persist_directory"], 
        storage_config["faiss_cache_directory"]
    ]
    
    print("Setting up storage directories for IntelliClaim...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Render deployment: {storage_config['render_deployment']}")
    print()
    
    # Create directories
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✓ Created/verified directory: {directory}")
        except Exception as e:
            print(f"✗ Error creating directory {directory}: {e}")
            return False
    
    # Verify write permissions
    print("\nVerifying write permissions...")
    for directory in directories:
        try:
            test_file = Path(directory) / ".test_write"
            test_file.write_text("test")
            test_file.unlink()  # Clean up test file
            print(f"✓ Write permission verified for: {directory}")
        except Exception as e:
            print(f"✗ Write permission failed for {directory}: {e}")
            return False
    
    # Display storage configuration
    print("\nStorage Configuration:")
    print(f"  Upload Directory: {storage_config['upload_directory']}")
    print(f"  ChromaDB Directory: {storage_config['chroma_persist_directory']}")
    print(f"  FAISS Cache Directory: {storage_config['faiss_cache_directory']}")
    print(f"  Max File Size: {storage_config['max_file_size'] / (1024*1024):.1f} MB")
    print(f"  Allowed File Types: {', '.join(storage_config['allowed_file_types'])}")
    
    print("\n✓ Storage setup completed successfully!")
    return True

def validate_environment():
    """Validate environment variables and configuration"""
    print("Validating environment configuration...")
    
    required_vars = ["GOOGLE_API_KEY"]
    optional_vars = ["ENVIRONMENT", "RENDER", "PORT", "CHROMA_PERSIST_DIR", "UPLOAD_DIR", "FAISS_CACHE_DIR"]
    
    # Check required variables
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"✗ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    # Check optional variables
    print("Environment variables:")
    for var in required_vars + optional_vars:
        value = os.getenv(var, "not set")
        if var == "GOOGLE_API_KEY":
            # Mask API key for security
            display_value = f"{value[:8]}..." if len(value) > 8 else "***"
        else:
            display_value = value
        print(f"  {var}: {display_value}")
    
    print("✓ Environment validation completed!")
    return True

def main():
    """Main function to run storage setup"""
    print("=" * 60)
    print("IntelliClaim Storage Setup for Render Deployment")
    print("=" * 60)
    
    # Validate environment first
    if not validate_environment():
        print("\n❌ Environment validation failed. Please check your configuration.")
        sys.exit(1)
    
    # Setup storage
    if not setup_storage():
        print("\n❌ Storage setup failed. Please check permissions and paths.")
        sys.exit(1)
    
    print("\n🎉 All setup tasks completed successfully!")
    print("\nNext steps:")
    print("1. Ensure your backend service is configured to use these directories")
    print("2. Test file uploads and document processing")
    print("3. Monitor storage usage and performance")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
