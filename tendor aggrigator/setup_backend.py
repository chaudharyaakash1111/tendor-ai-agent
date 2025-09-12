"""
Setup script for Tender Aggregator Backend.
This script helps install dependencies and setup the environment.
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend_requirements.txt"])
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    return True

def download_spacy_model():
    """Download the spaCy English model."""
    print("Downloading spaCy English model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ spaCy English model downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        return False
    return True

def setup_mongodb():
    """Provide instructions for MongoDB setup."""
    print("\n📝 MongoDB Setup Instructions:")
    print("1. Install MongoDB Community Server from https://www.mongodb.com/try/download/community")
    print("2. Start MongoDB service")
    print("3. The application will automatically connect to MongoDB at mongodb://localhost:27017/")
    return True

def main():
    """Main setup function."""
    print("🔧 Tender Aggregator Backend Setup")
    print("=" * 40)
    
    # Install Python dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Download spaCy model
    if not download_spacy_model():
        sys.exit(1)
    
    # Provide MongoDB setup instructions
    setup_mongodb()
    
    print("\n✅ Setup completed successfully!")
    print("\n🚀 To start the backend server, run:")
    print("   python run_backend.py")
    print("\n🧪 To test the backend, run:")
    print("   python test_backend.py")

if __name__ == "__main__":
    main()