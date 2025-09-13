#!/usr/bin/env python3
"""
Setup script for Plaza Backend
"""

import os
import subprocess
import sys

def install_requirements():
    """Install Python requirements."""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write("NEWS_API_KEY=your_news_api_key_here\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=True\n")
        print("✅ .env file created!")
        print("⚠️  Please edit .env file and add your NewsAPI key from https://newsapi.org/")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function."""
    print("🚀 Setting up Plaza Backend...")
    
    if not install_requirements():
        return
    
    create_env_file()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Get a free NewsAPI key from https://newsapi.org/")
    print("2. Edit the .env file and add your API key")
    print("3. Run: python app.py")
    print("4. The backend will be available at http://localhost:5000")

if __name__ == "__main__":
    main()