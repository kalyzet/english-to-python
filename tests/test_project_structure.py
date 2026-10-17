"""
Test untuk memastikan struktur project bekerja dengan baik
"""

import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_project_structure():
    """Test bahwa semua direktori utama ada"""
    expected_dirs = [
        'ttc',
        'ttc/engine',
        'tests',
        'tests/unit',
        'tests/property',
        'tests/integration',
        'docs',
    ]

    for dir_path in expected_dirs:
        path = os.path.join(ROOT, dir_path)
        assert os.path.exists(path), f"Directory {dir_path} tidak ditemukan"
        assert os.path.isdir(path), f"{dir_path} bukan directory"


def test_required_files():
    """Test bahwa file-file penting ada"""
    expected_files = [
        'pyproject.toml',
        'README.md',
        'pytest.ini',
        '.gitignore',
    ]

    for file_path in expected_files:
        path = os.path.join(ROOT, file_path)
        assert os.path.exists(path), f"File {file_path} tidak ditemukan"
        assert os.path.isfile(path), f"{file_path} bukan file"


def test_package_importable():
    """Test bahwa paket ttc bisa diimport"""
    try:
        import ttc
        from ttc import TranslationEngine, PatternType, TranslationResult
    except ImportError as e:
        pytest.fail(f"Tidak bisa import paket ttc: {e}")

    assert ttc.__version__


def test_cli_executable():
    """Test bahwa CLI `python -m ttc` bisa dijalankan"""
    result = subprocess.run(
        [sys.executable, '-m', 'ttc', 'set age to 25'],
        capture_output=True, text=True, timeout=30, cwd=ROOT,
    )

    assert result.returncode == 0, f"CLI gagal dijalankan: {result.stderr}"
    assert 'age = 25' in result.stdout
