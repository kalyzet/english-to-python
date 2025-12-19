"""
Test untuk memastikan struktur project bekerja dengan baik
"""

import os
import sys
import pytest

def test_project_structure():
    """Test bahwa semua direktori utama ada"""
    expected_dirs = [
        'src',
        'src/models',
        'src/core', 
        'src/services',
        'src/gui',
        'tests',
        'tests/unit',
        'tests/property',
        'tests/integration'
    ]
    
    for dir_path in expected_dirs:
        assert os.path.exists(dir_path), f"Directory {dir_path} tidak ditemukan"
        assert os.path.isdir(dir_path), f"{dir_path} bukan directory"

def test_required_files():
    """Test bahwa file-file penting ada"""
    expected_files = [
        'main.py',
        'requirements.txt',
        'setup.py',
        'README.md',
        'pytest.ini',
        '.gitignore'
    ]
    
    for file_path in expected_files:
        assert os.path.exists(file_path), f"File {file_path} tidak ditemukan"
        assert os.path.isfile(file_path), f"{file_path} bukan file"

def test_python_path():
    """Test bahwa src directory bisa diimport"""
    # Add src to path seperti di main.py
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Test import packages
    try:
        import models
        import core
        import services
        import gui
    except ImportError as e:
        pytest.fail(f"Tidak bisa import package: {e}")

def test_main_executable():
    """Test bahwa main.py bisa dijalankan"""
    import subprocess
    import sys
    
    result = subprocess.run([sys.executable, 'main.py'], 
                          capture_output=True, text=True, timeout=10)
    
    # Main.py should run without errors
    assert result.returncode == 0, f"main.py gagal dijalankan: {result.stderr}"
    assert "English to Python Translator" in result.stdout
    assert "Application structure initialized successfully!" in result.stdout