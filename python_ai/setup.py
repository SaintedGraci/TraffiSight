"""
Setup script for TraffiSight AI
Helps with initial setup and configuration
"""

import sys
import subprocess
from pathlib import Path
import shutil


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60 + "\n")


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher is required!")
        return False
    
    print("✅ Python version is compatible")
    return True


def create_virtual_environment():
    """Create virtual environment"""
    print_header("Creating Virtual Environment")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("Recreate it? (y/n): ")
        if response.lower() == 'y':
            print("Removing existing virtual environment...")
            shutil.rmtree(venv_path)
        else:
            print("Using existing virtual environment")
            return True
    
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False


def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    # Determine pip path
    if sys.platform == "win32":
        pip_path = Path("venv/Scripts/pip.exe")
    else:
        pip_path = Path("venv/bin/pip")
    
    if not pip_path.exists():
        print("❌ Virtual environment pip not found")
        print("Please activate virtual environment first")
        return False
    
    print("Upgrading pip...")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=False)
    
    print("\nInstalling requirements...")
    print("This may take several minutes...")
    
    try:
        subprocess.run(
            [str(pip_path), "install", "-r", "requirements.txt"],
            check=True
        )
        print("\n✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Failed to install some dependencies")
        print("Try manual installation: pip install -r requirements.txt")
        return False


def setup_directories():
    """Create required directories"""
    print_header("Setting Up Directories")
    
    directories = [
        "logs",
        "output",
        "output/frames",
        "output/thumbnails",
        "output/detections",
        "output/results",
        "models",
        "temp"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {directory}")
        else:
            print(f"  Exists: {directory}")
    
    print("\n✅ All directories ready")
    return True


def setup_environment_file():
    """Setup .env file"""
    print_header("Setting Up Environment File")
    
    env_path = Path(".env")
    example_path = Path(".env.example")
    
    if env_path.exists():
        print("⚠️  .env file already exists")
        return True
    
    if example_path.exists():
        shutil.copy(example_path, env_path)
        print("✅ Created .env from .env.example")
        print("⚠️  Please edit .env with your configuration")
    else:
        print("⚠️  .env.example not found, skipping")
    
    return True


def verify_installation():
    """Verify installation by importing modules"""
    print_header("Verifying Installation")
    
    modules_to_check = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("yaml", "PyYAML"),
        ("colorlog", "ColorLog"),
        ("tqdm", "TQDM"),
    ]
    
    all_ok = True
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} - NOT INSTALLED")
            all_ok = False
    
    if all_ok:
        print("\n✅ All required modules are installed")
    else:
        print("\n❌ Some modules are missing")
    
    return all_ok


def print_next_steps():
    """Print next steps for user"""
    print_header("Setup Complete!")
    
    print("Next steps:")
    print("\n1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Edit configuration (optional):")
    print("   Edit .env and config/config.yaml")
    
    print("\n3. Test installation:")
    print("   python main.py test -i path/to/video.mp4")
    
    print("\n4. Read documentation:")
    print("   See README.md for usage examples")
    
    print("\n" + "="*60)


def main():
    """Main setup function"""
    print_header("TraffiSight AI - Setup Script")
    print("This script will set up your development environment")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment
    if not create_virtual_environment():
        return 1
    
    print("\n⚠️  IMPORTANT: After setup completes, you must:")
    print("   1. Activate the virtual environment")
    print("   2. Run this script again from within the venv")
    print("\nContinue? (y/n): ", end="")
    
    if input().lower() != 'y':
        print("Setup cancelled")
        return 0
    
    # Setup directories
    setup_directories()
    
    # Setup environment file
    setup_environment_file()
    
    # Ask about installing dependencies
    print("\n" + "-"*60)
    print("Install dependencies now?")
    print("This requires an active virtual environment")
    print("-"*60)
    response = input("Install dependencies? (y/n): ")
    
    if response.lower() == 'y':
        if not install_dependencies():
            print("\n⚠️  Please activate venv and run: pip install -r requirements.txt")
        else:
            verify_installation()
    
    # Print next steps
    print_next_steps()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
