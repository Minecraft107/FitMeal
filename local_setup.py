"""
Local setup script for VS Code environment.
Run this script to create a .env file with required environment variables.
"""

import os
import secrets
import getpass

def create_local_env():
    """Create a .env file with required environment variables for local development."""
    env_file = '.env'
    
    # If .env file already exists, ask before overwriting
    if os.path.exists(env_file):
        print(f"\n{env_file} already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Aborting...")
            return
    
    # Generate a secret key
    session_secret = secrets.token_hex(16)
    
    # Get MongoDB URL (optional)
    print("\nMongoDB Setup (optional, press Enter to skip):")
    use_mongodb = input("Do you want to set up MongoDB? (y/n, default 'n'): ").lower()
    
    mongodb_uri = None
    if use_mongodb == 'y':
        mongo_user = input("Enter MongoDB username: ")
        mongo_pass = getpass.getpass("Enter MongoDB password: ")
        mongo_host = input("Enter MongoDB host (default 'localhost'): ") or 'localhost'
        mongo_port = input("Enter MongoDB port (default '27017'): ") or '27017'
        mongo_db = input("Enter MongoDB database name (default 'nutrition_assistant'): ") or 'nutrition_assistant'
        
        # Create MongoDB URI
        mongodb_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/{mongo_db}"
    
    # Get API keys for chat functionality
    print("\nAI Chat Functionality Setup:")
    print("You need a Google Gemini API key for the chatbot functionality.")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    gemini_key = getpass.getpass("Enter your Gemini API key: ")
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(f"# Flask Secret Key\n")
        f.write(f"SESSION_SECRET={session_secret}\n\n")
        
        if mongodb_uri:
            f.write(f"# MongoDB Config\n")
            f.write(f"MONGODB_URI={mongodb_uri}\n\n")
        
        f.write(f"# API Keys for AI Chat Functionality\n")
        if gemini_key:
            f.write(f"GEMINI_API_KEY={gemini_key}\n")
    
    print(f"\n{env_file} created successfully!")
    print("\nNotes:")
    print("1. Run the application with: python main.py")
    print("2. Access the application at: http://localhost:5000")

if __name__ == "__main__":
    create_local_env()