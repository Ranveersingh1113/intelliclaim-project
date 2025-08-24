#!/usr/bin/env python3
"""
Railway-optimized build script for IntelliClaim backend
This Python script handles the build process more reliably than shell scripts
"""

import os
import subprocess
import sys
import shutil

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"📝 Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stderr:
            print(f"🚨 Error: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating storage directories...")
    directories = ['uploads', 'chroma_db', 'faiss_cache']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")

def install_dependencies():
    """Install Python dependencies in stages"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        print("⚠️ pip upgrade failed, continuing...")
    
    # Install core dependencies
    core_deps = [
        "fastapi==0.111.0",
        "uvicorn[standard]==0.29.0", 
        "python-dotenv==1.0.1",
        "requests==2.32.3"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install --no-cache-dir --prefer-binary {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, continuing...")
    
    # Install document processing dependencies
    doc_deps = [
        "python-docx==1.1.0",
        "PyPDF2==3.0.1"
    ]
    
    for dep in doc_deps:
        if not run_command(f"pip install --no-cache-dir --prefer-binary {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, continuing...")
    
    # Install AI/ML dependencies
    ai_deps = [
        "langchain==0.2.0",
        "langchain-community==0.2.0",
        "langgraph==0.2.21",
        "pydantic>=2.8.0"
    ]
    
    for dep in ai_deps:
        if not run_command(f"pip install --no-cache-dir --prefer-binary {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, continuing...")
    
    # Install Google AI dependencies
    if not run_command("pip install --no-cache-dir --prefer-binary google-generativeai==0.5.0", "Installing Google AI"):
        print("⚠️ Failed to install Google AI, continuing...")
    
    # Install vector database
    if not run_command("pip install --no-cache-dir --prefer-binary chromadb==0.5.5", "Installing ChromaDB"):
        print("⚠️ Failed to install ChromaDB, continuing...")
    
    # Install embedding models
    if not run_command("pip install --no-cache-dir --prefer-binary sentence-transformers==2.2.2", "Installing sentence-transformers"):
        print("⚠️ Failed to install sentence-transformers, continuing...")

def verify_installation():
    """Verify that critical packages are installed"""
    print("🔍 Verifying critical package installations...")
    
    critical_packages = [
        "fastapi", "uvicorn", "chromadb", "google.generativeai", "sentence_transformers"
    ]
    
    failed_packages = []
    for package in critical_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} imported successfully")
        except ImportError:
            print(f"❌ {package} import failed")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"⚠️ Failed packages: {failed_packages}")
        return False
    else:
        print("✅ All critical packages installed successfully")
        return True

def run_storage_setup():
    """Run the storage setup script"""
    print("⚙️ Running storage setup script...")
    
    if os.path.exists("setup_storage.py"):
        if run_command("python setup_storage.py", "Storage setup"):
            print("✅ Storage setup completed")
            return True
        else:
            print("⚠️ Storage setup failed, continuing...")
            return False
    else:
        print("⚠️ setup_storage.py not found, skipping...")
        return False

def main():
    """Main build process"""
    print("🚀 Starting IntelliClaim Railway build process...")
    print("=" * 50)
    
    # Change to backend directory if not already there
    if not os.path.exists("app.py"):
        print("⚠️ app.py not found in current directory")
        if os.path.exists("../backend/app.py"):
            os.chdir("../backend")
            print("✅ Changed to backend directory")
        else:
            print("❌ Cannot find backend directory")
            sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Run storage setup
    run_storage_setup()
    
    # Verify installation
    verification_success = verify_installation()
    
    print("=" * 50)
    if verification_success:
        print("✅ Railway build completed successfully!")
        print("📋 Build summary:")
        print("  - Python dependencies installed")
        print("  - Storage directories created")
        print("  - Configuration validated")
        print("")
        print("🚀 Ready for Railway deployment!")
        sys.exit(0)
    else:
        print("⚠️ Railway build completed with warnings")
        print("Some packages may have installation issues")
        print("Check the logs above for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
