#!/usr/bin/env python3
"""
Setup script untuk English to Python Translator
Membuat virtual environment dan install dependencies
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} berhasil")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("English to Python Translator - Setup Environment")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Error: Python 3.8 atau lebih tinggi diperlukan")
        sys.exit(1)
    
    print(f"✓ Python {sys.version} detected")
    
    # Create virtual environment
    venv_name = "venv"
    if not os.path.exists(venv_name):
        if not run_command(f"{sys.executable} -m venv {venv_name}", "Membuat virtual environment"):
            sys.exit(1)
    else:
        print(f"✓ Virtual environment '{venv_name}' sudah ada")
    
    # Determine activation command based on OS
    if platform.system() == "Windows":
        activate_cmd = f"{venv_name}\\Scripts\\activate"
        pip_cmd = f"{venv_name}\\Scripts\\pip"
    else:
        activate_cmd = f"source {venv_name}/bin/activate"
        pip_cmd = f"{venv_name}/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrade pip"):
        sys.exit(1)
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Install dependencies"):
        sys.exit(1)
    
    # Download NLTK data
    print("\nDownloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print("✓ NLTK data downloaded")
    except Exception as e:
        print(f"⚠ Warning: Could not download NLTK data: {e}")
        print("  You can download it later by running:")
        print("  python -c \"import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')\"")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo activate the virtual environment:")
    print(f"  {activate_cmd}")
    print("\nTo run the application:")
    print("  python main.py")
    print("\nTo run tests:")
    print("  pytest")

if __name__ == "__main__":
    main()