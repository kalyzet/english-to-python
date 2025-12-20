#!/usr/bin/env python3
"""
Debug script untuk mereproduksi error "unterminated string literal"
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set test mode to avoid GUI
os.environ['PYTEST_CURRENT_TEST'] = 'true'

def debug_string_error():
    """Debug error yang terjadi dengan input user"""
    
    try:
        from services.translation_engine import TranslationEngine
        
        engine = TranslationEngine()
        
        print("🐛 DEBUG: UNTERMINATED STRING LITERAL ERROR")
        print("=" * 50)
        print()
        
        # Input yang menyebabkan error
        problematic_inputs = [
            "set student_name to Alice",
            "set math_score to 85", 
            "set english_score to 92",
            "if math_score greater than 80 then print good_math else print poor_math",
            "if english_score greater than 90 then print excellent_english else print good_english"
        ]
        
        print("📋 INPUT SEQUENCE YANG BERMASALAH:")
        for i, input_text in enumerate(problematic_inputs, 1):
            print(f"{i}. {input_text}")
        print()
        
        all_code = []
        
        for i, input_text in enumerate(problematic_inputs, 1):
            print(f"🔍 Testing Input {i}: {input_text}")
            print("-" * 40)
            
            result = engine.translate(input_text)
            
            if result.success:
                print("✅ Translation Success!")
                print("Generated Code:")
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
                
                all_code.append(result.python_code)
                
                # Test syntax validation
                try:
                    compile(result.python_code, '<string>', 'exec')
                    print("✅ Syntax Valid!")
                except SyntaxError as e:
                    print(f"❌ SYNTAX ERROR: {e}")
                    print(f"   Line {e.lineno}: {e.text}")
                    print(f"   Error: {e.msg}")
                    
                    # Show the problematic code with line numbers
                    print("\n📝 PROBLEMATIC CODE:")
                    for j, line in enumerate(result.python_code.split('\n'), 1):
                        marker = ">>> " if j == e.lineno else "    "
                        print(f"{marker}{j}: {line}")
                    
                    return  # Stop at first error
                    
            else:
                print("❌ Translation Failed!")
                print(f"Error: {result.error_message}")
                return
            
            print()
        
        # Test combined code
        print("🔄 TESTING COMBINED CODE:")
        print("-" * 30)
        
        combined_code = '\n'.join(all_code)
        print("Combined Code:")
        for i, line in enumerate(combined_code.split('\n'), 1):
            print(f"    {i}: {line}")
        
        try:
            compile(combined_code, '<string>', 'exec')
            print("✅ Combined code syntax is valid!")
        except SyntaxError as e:
            print(f"❌ COMBINED CODE SYNTAX ERROR: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            print(f"   Error: {e.msg}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_specific_problematic_cases():
    """Test kasus-kasus spesifik yang mungkin bermasalah"""
    
    try:
        from services.translation_engine import TranslationEngine
        
        engine = TranslationEngine()
        
        print("🧪 TEST: KASUS SPESIFIK YANG BERMASALAH")
        print("=" * 45)
        print()
        
        test_cases = [
            {
                "title": "String dengan underscore",
                "input": "if math_score greater than 80 then print good_math else print poor_math"
            },
            {
                "title": "String dengan underscore 2",
                "input": "if english_score greater than 90 then print excellent_english else print good_english"
            },
            {
                "title": "Print dengan underscore",
                "input": "if age greater than 18 then print good_result"
            }
        ]
        
        for test_case in test_cases:
            print(f"🔍 {test_case['title']}")
            print(f"Input: {test_case['input']}")
            print("-" * 40)
            
            result = engine.translate(test_case['input'])
            
            if result.success:
                print("Generated Code:")
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
                
                # Test syntax
                try:
                    compile(result.python_code, '<string>', 'exec')
                    print("✅ Syntax Valid!")
                except SyntaxError as e:
                    print(f"❌ SYNTAX ERROR: {e}")
                    print(f"   Problem: {e.msg}")
                    
                    # Show character-by-character analysis
                    if e.text:
                        print(f"   Problematic line: '{e.text.strip()}'")
                        print(f"   Character analysis:")
                        for i, char in enumerate(e.text):
                            if char in ['"', "'"]:
                                print(f"     Position {i}: '{char}' (quote)")
                            elif char == '\n':
                                print(f"     Position {i}: '\\n' (newline)")
                            else:
                                print(f"     Position {i}: '{char}'")
                    
            else:
                print(f"❌ Translation Failed: {result.error_message}")
            
            print()
            print("=" * 45)
            print()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    debug_string_error()
    test_specific_problematic_cases()