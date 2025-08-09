#!/usr/bin/env python3
"""
ClauseMind Cloud - Startup Script
Run this script to start the ClauseMind Cloud application and set up the environment.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import langchain
        import sentence_transformers
        import pinecone
        import cloudinary
        import PyPDF2
        import google.generativeai
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Creating .env file with default values...")
        
        env_content = """# ClauseMind Cloud Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=models/gemini-1.5-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5

# Cloud storage settings
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Pinecone settings
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=assurio-documents

# Hugging Face settings (optional)
HUGGINGFACE_API_KEY=your_huggingface_api_key
USE_REMOTE_EMBEDDINGS=false

# Storage mode
STORAGE_MODE=cloud
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file")
        print("⚠️  Please update all API keys in .env file with your actual credentials")
        return False
    
    # Check if API keys are set
    with open(env_file, 'r') as f:
        content = f.read()
        missing_keys = []
        
        required_keys = [
            'GEMINI_API_KEY',
            'CLOUDINARY_CLOUD_NAME',
            'CLOUDINARY_API_KEY', 
            'CLOUDINARY_API_SECRET',
            'PINECONE_API_KEY'
        ]
        
        for key in required_keys:
            if f'{key}=your_' in content or f'{key}=' in content:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"⚠️  Please update these API keys in .env file: {', '.join(missing_keys)}")
            return False
    
    print("✅ Environment configuration looks good")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'frontend', 'templates']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting ClauseMind Cloud server...")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def open_browser():
    """Open browser to the application"""
    try:
        time.sleep(3)  # Wait for server to start
        webbrowser.open("http://localhost:8000")
        webbrowser.open("http://localhost:8000/docs")
        print("🌐 Opened browser to application")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")

def main():
    """Main startup function"""
    print("🧠 ClauseMind Cloud - Intelligent Clause Retriever & Decision System")
    print("=" * 70)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment
    env_ok = check_env_file()
    
    # Create directories
    create_directories()
    
    print("\n📋 Quick Start Guide:")
    print("1. Get your API keys from:")
    print("   - Google Gemini: https://makersuite.google.com/app/apikey")
    print("   - Cloudinary: https://cloudinary.com")
    print("   - Pinecone: https://pinecone.io")
    print("   - Hugging Face (optional): https://huggingface.co")
    print("2. Update the API keys in .env file")
    print("3. Upload a PDF document via the web interface")
    print("4. Start querying the system!")
    
    if not env_ok:
        print("\n⚠️  Please configure your API keys before starting the server")
        print("📖 See CLOUD_DEPLOYMENT_GUIDE.md for detailed setup instructions")
        return
    
    print("\n🎯 Starting application...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🌐 Web Interface will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 