"""
Installation Guide for Python 3.14.0

This script provides step-by-step installation instructions.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.14 or compatible."""
    version_info = sys.version_info
    print(f"✓ Detected Python: {version_info.major}.{version_info.minor}.{version_info.micro}")
    
    if version_info >= (3, 10):
        print(f"✓ Python version is compatible (3.10+)")
        return True
    else:
        print(f"✗ Python 3.10+ required. Current: {version_info.major}.{version_info.minor}")
        return False


def create_virtual_environment():
    """Create a Python virtual environment."""
    print("\n📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created successfully")
        
        # Determine activation script path
        if sys.platform == "win32":
            activate_script = Path("venv/Scripts/activate.bat")
            activation_command = f"venv\\Scripts\\activate"
        else:
            activate_script = Path("venv/bin/activate")
            activation_command = f"source venv/bin/activate"
        
        print(f"\n📝 To activate virtual environment, run:")
        print(f"   {activation_command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False


def upgrade_pip():
    """Upgrade pip to latest version."""
    print("\n🔧 Upgrading pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True
        )
        print("✓ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to upgrade pip: {e}")
        return False


def install_dependencies():
    """Install project dependencies from requirements.txt."""
    print("\n📥 Installing dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print(f"✗ requirements.txt not found at {requirements_file.absolute()}")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure virtual environment is activated")
        print("   2. Check internet connection")
        print("   3. Try: pip install --upgrade setuptools wheel")
        print("   4. Then: pip install -r requirements.txt")
        return False


def initialize_database():
    """Initialize the SQLite database."""
    print("\n🗄️  Initializing database...")
    try:
        from app.database.db import init_db
        init_db()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        print("\n💡 Troubleshooting:")
        print("   Make sure you're in the 'backend' directory")
        print("   And the virtual environment is activated")
        return False


def create_env_file():
    """Create .env file from .env.example."""
    print("\n📝 Setting up .env file...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print(f"✗ .env.example not found")
        return False
    
    if env_file.exists():
        print(f"✓ .env already exists (skipping)")
        return True
    
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✓ .env file created from .env.example")
        print(f"  Location: {env_file.absolute()}")
        print(f"  ⚠️  Remember to update SECRET_KEY for production!")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env: {e}")
        return False


def print_next_steps():
    """Print next steps for running the application."""
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("="*60)
    
    print("\n📋 Next steps:")
    print("\n1️⃣  Activate virtual environment (if not already active):")
    
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2️⃣  Run the FastAPI server:")
    print("   uvicorn app.main:app --reload")
    
    print("\n3️⃣  Open in browser:")
    print("   http://localhost:8000/api/docs  (Swagger UI)")
    print("   http://localhost:8000/api/redoc (ReDoc)")
    
    print("\n4️⃣  Run tests:")
    print("   pytest")
    
    print("\n5️⃣  Run with coverage:")
    print("   pytest --cov=app --cov-report=html")
    
    print("\n📚 Documentation:")
    print("   - See README.md for detailed documentation")
    print("   - See IMPLEMENTATION_SUMMARY.md for architecture overview")
    print("   - See QUICK_REFERENCE.md for quick reference")


def main():
    """Run complete installation process."""
    print("="*60)
    print("🚀 Cash Management System - Python 3.14 Installation")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    print("\n⚠️  Make sure to activate the virtual environment!")
    print("   Then run this script again, or continue manually")
    
    # Ask if user activated venv
    response = input("\nHave you activated the virtual environment? (yes/no): ").lower()
    if response not in ['yes', 'y']:
        print("Please activate the virtual environment first:")
        if sys.platform == "win32":
            print("  venv\\Scripts\\activate")
        else:
            print("  source venv/bin/activate")
        return False
    
    # Upgrade pip
    if not upgrade_pip():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Initialize database
    if not initialize_database():
        print("\n💡 You can initialize database manually later:")
        print("   python -c \"from app.database.db import init_db; init_db()\"")
    
    # Print next steps
    print_next_steps()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
