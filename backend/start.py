#!/usr/bin/env python3
"""
Legal Document AI Assistant - Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")

def check_virtual_environment():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        print("Recommendation: Create and activate a virtual environment")
        return False

def check_env_file():
    """Check if .env file exists"""
    if Path('.env').exists():
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found!")
        print("Please copy .env.template to .env and add your API keys")
        return False

def check_dependencies():
    required_packages = ['fastapi', 'uvicorn', 'langchain', 'python-dotenv']
    missing_packages = []

    for package in required_packages:
        # Correct import name for python-dotenv
        import_name = 'dotenv' if package == 'python-dotenv' else package.replace('-', '_')

        try:
            __import__(import_name)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")

    if missing_packages:
        print("\n📦 To install missing packages, run:")
        print("pip install -r requirements_updated.txt")
        return False

    return True


def check_directories():
    """Create necessary directories"""
    directories = ['uploads', 'static', 'templates']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory {directory} ready")

def start_application():
    """Start the FastAPI application"""
    print("\n🚀 Starting Legal Document AI Assistant...")
    print("🌐 Application will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the application\n")

    try:
        # Start the application
        os.system("python main.py")
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped. Thank you for using Legal Document AI Assistant!")

def main():
    """Main startup function"""
    print("=" * 60)
    print("📋 LEGAL DOCUMENT AI ASSISTANT - STARTUP CHECK")
    print("=" * 60)

    # Run all checks
    check_python_version()
    venv_ok = check_virtual_environment()
    env_ok = check_env_file()
    deps_ok = check_dependencies()
    check_directories()

    print("\n" + "=" * 60)

    # Decide whether to start the application
    if env_ok and deps_ok:
        print("✅ All checks passed!")
        start_application()
    else:
        print("❌ Please fix the issues above before starting the application.")
        print("\n📖 See README.md for detailed setup instructions.")

        if not env_ok:
            print("\n🔧 Quick fix for .env file:")
            print("1. Copy .env.template to .env")
            print("2. Edit .env and add your API keys:")
            print("   - GROQ_API_KEY=your_key_here")
            print("   - GEMINI_API_KEY=your_key_here")

        if not deps_ok:
            print("\n🔧 Quick fix for dependencies:")
            print("pip install -r requirements_updated.txt")

if __name__ == "__main__":
    main()
