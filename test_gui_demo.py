#!/usr/bin/env python3
"""
Demo script untuk test GUI English to Python Translator
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from services.translation_engine import TranslationEngine

def test_translations():
    """Test berbagai jenis translasi"""
    engine = TranslationEngine()
    
    test_cases = [
        "set x to 10",
        "set y to 5", 
        "add x and y",
        "multiply result by 2",
        "create list with 1, 2, 3",
        "if x greater than 5 then print hello"
    ]
    
    print("=== English to Python Translator Demo ===\n")
    
    for i, instruction in enumerate(test_cases, 1):
        print(f"{i}. Input: {instruction}")
        result = engine.translate(instruction)
        
        if result.success:
            print(f"   Output: {result.python_code}")
            print(f"   Repr: {repr(result.python_code)}")
        else:
            print(f"   Error: {result.error_message}")
        print()

if __name__ == "__main__":
    test_translations()