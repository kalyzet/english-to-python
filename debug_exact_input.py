#!/usr/bin/env python3
"""
Debug script untuk test input persis seperti yang diberikan user
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set test mode to avoid GUI
os.environ['PYTEST_CURRENT_TEST'] = 'true'

def debug_exact_user_input():
    """Debug dengan input persis seperti yang diberikan user"""
    
    try:
        from services.translation_engine import TranslationEngine
        
        engine = TranslationEngine()
        
        print("🐛 DEBUG: INPUT PERSIS SEPERTI USER")
        print("=" * 40)
        print()
        
        # Input persis seperti yang diberikan user (tanpa spasi/newline)
        user_input = "set student_name to Aliceset math_score to 85set english_score to 92if math_score greater than 80 then print good_math else print poor_mathif english_score greater than 90 then print excellent_english else print good_english"
        
        print("📝 USER INPUT (persis):")
        print(f"'{user_input}'")
        print()
        print("📏 Length:", len(user_input))
        print("🔍 Character analysis:")
        for i, char in enumerate(user_input):
            if i < 100:  # Show first 100 chars
                if char == ' ':
                    print(f"  {i}: [SPACE]")
                elif char == '\n':
                    print(f"  {i}: [NEWLINE]")
                elif char == '\t':
                    print(f"  {i}: [TAB]")
                else:
                    print(f"  {i}: '{char}'")
        print()
        
        # Test translation
        print("🔄 TRANSLATING...")
        result = engine.translate(user_input)
        
        if result.success:
            print("✅ Translation Success!")
            print("Generated Code:")
            print("```python")
            print(result.python_code)
            print("```")
            print()
            
            # Test syntax validation
            try:
                compile(result.python_code, '<string>', 'exec')
                print("✅ Syntax Valid!")
            except SyntaxError as e:
                print(f"❌ SYNTAX ERROR FOUND!")
                print(f"   Error: {e.msg}")
                print(f"   Line {e.lineno}: {e.text}")
                print(f"   Position: {e.offset}")
                print()
                
                # Show the problematic code with line numbers
                print("📝 GENERATED CODE WITH LINE NUMBERS:")
                for j, line in enumerate(result.python_code.split('\n'), 1):
                    marker = ">>> " if j == e.lineno else "    "
                    print(f"{marker}{j}: '{line}'")
                print()
                
                # Character analysis of problematic line
                if e.text:
                    print("🔍 CHARACTER ANALYSIS OF PROBLEMATIC LINE:")
                    for k, char in enumerate(e.text):
                        if char in ['"', "'"]:
                            print(f"     {k}: '{char}' (QUOTE)")
                        elif char == '\n':
                            print(f"     {k}: '\\n' (NEWLINE)")
                        elif char == ' ':
                            print(f"     {k}: [SPACE]")
                        else:
                            print(f"     {k}: '{char}'")
                
        else:
            print("❌ Translation Failed!")
            print(f"Error: {result.error_message}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_multiline_input():
    """Test dengan input yang dipisah dengan newline"""
    
    try:
        from services.translation_engine import TranslationEngine
        
        engine = TranslationEngine()
        
        print("🧪 TEST: MULTILINE INPUT")
        print("=" * 30)
        print()
        
        # Input dengan newline
        multiline_input = """set student_name to Alice
set math_score to 85
set english_score to 92
if math_score greater than 80 then print good_math else print poor_math
if english_score greater than 90 then print excellent_english else print good_english"""
        
        print("📝 MULTILINE INPUT:")
        print("```")
        print(multiline_input)
        print("```")
        print()
        
        # Test translation
        result = engine.translate(multiline_input)
        
        if result.success:
            print("✅ Translation Success!")
            print("Generated Code:")
            print("```python")
            print(result.python_code)
            print("```")
            
            # Test syntax
            try:
                compile(result.python_code, '<string>', 'exec')
                print("✅ Syntax Valid!")
            except SyntaxError as e:
                print(f"❌ SYNTAX ERROR: {e}")
                
        else:
            print("❌ Translation Failed!")
            print(f"Error: {result.error_message}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    debug_exact_user_input()
    test_multiline_input()