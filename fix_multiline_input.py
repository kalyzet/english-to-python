#!/usr/bin/env python3
"""
Fix untuk menangani multiple statements dalam satu input
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set test mode to avoid GUI
os.environ['PYTEST_CURRENT_TEST'] = 'true'

def split_multiline_input(input_text: str) -> list:
    """Split multiline input into individual statements"""
    
    # Split by newlines first
    lines = input_text.strip().split('\n')
    statements = []
    
    for line in lines:
        line = line.strip()
        if line:  # Skip empty lines
            statements.append(line)
    
    # If no newlines, try to detect multiple statements in one line
    if len(statements) == 1:
        single_line = statements[0]
        
        # Look for patterns that indicate multiple statements
        # Pattern: "set ... to ..." followed by another "set" or "if"
        import re
        
        # Split on common statement beginnings
        patterns = [
            r'(?=\bset\s+\w+\s+to\s+)',  # Before "set variable to"
            r'(?=\bif\s+\w+\s+)',        # Before "if variable"
            r'(?=\bwhen\s+\w+\s+)',      # Before "when variable"
            r'(?=\bcreate\s+)',          # Before "create"
            r'(?=\badd\s+\w+\s+and\s+)', # Before "add X and Y"
        ]
        
        # Try each pattern
        for pattern in patterns:
            parts = re.split(pattern, single_line)
            if len(parts) > 1:
                # Filter out empty parts and clean up
                statements = [part.strip() for part in parts if part.strip()]
                break
    
    return statements

def test_multiline_fix():
    """Test fix untuk multiline input"""
    
    try:
        from services.translation_engine import TranslationEngine
        from services.code_execution_service import CodeExecutionService
        
        engine = TranslationEngine()
        executor = CodeExecutionService()
        
        print("🔧 TEST: FIX MULTILINE INPUT")
        print("=" * 35)
        print()
        
        # Input bermasalah dari user
        problematic_input = """set student_name to Alice
set math_score to 85
set english_score to 92
if math_score greater than 80 then print good_math else print poor_math
if english_score greater than 90 then print excellent_english else print good_english"""
        
        print("📝 ORIGINAL PROBLEMATIC INPUT:")
        print("```")
        print(problematic_input)
        print("```")
        print()
        
        # Split into individual statements
        statements = split_multiline_input(problematic_input)
        
        print("🔪 SPLIT INTO STATEMENTS:")
        for i, stmt in enumerate(statements, 1):
            print(f"{i}. {stmt}")
        print()
        
        # Translate each statement
        all_code = []
        print("🔄 TRANSLATING EACH STATEMENT:")
        print("-" * 35)
        
        for i, stmt in enumerate(statements, 1):
            print(f"Statement {i}: {stmt}")
            
            result = engine.translate(stmt)
            if result.success:
                print("✅ Success")
                all_code.append(result.python_code)
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
            else:
                print(f"❌ Failed: {result.error_message}")
                return
            print()
        
        # Combine and test execution
        final_code = '\n'.join(all_code)
        
        print("🎯 FINAL COMBINED CODE:")
        print("```python")
        print(final_code)
        print("```")
        print()
        
        # Test execution
        print("▶️  EXECUTING...")
        exec_result = executor.execute_code(final_code)
        
        if exec_result.success:
            print("✅ EXECUTION SUCCESS!")
            if exec_result.has_output():
                print("📤 OUTPUT:")
                print(exec_result.get_combined_output())
            else:
                print("ℹ️  No output produced")
        else:
            print("❌ EXECUTION FAILED!")
            print(f"Error: {exec_result.get_combined_error()}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_single_line_multiple_statements():
    """Test input dengan multiple statements dalam satu line"""
    
    try:
        from services.translation_engine import TranslationEngine
        
        engine = TranslationEngine()
        
        print("🧪 TEST: SINGLE LINE MULTIPLE STATEMENTS")
        print("=" * 45)
        print()
        
        # Input seperti yang diberikan user (tanpa newline)
        single_line_input = "set student_name to Aliceset math_score to 85set english_score to 92if math_score greater than 80 then print good_math else print poor_mathif english_score greater than 90 then print excellent_english else print good_english"
        
        print("📝 SINGLE LINE INPUT:")
        print(f"'{single_line_input}'")
        print()
        
        # Split statements
        statements = split_multiline_input(single_line_input)
        
        print("🔪 DETECTED STATEMENTS:")
        for i, stmt in enumerate(statements, 1):
            print(f"{i}. {stmt}")
        print()
        
        # Translate each
        for i, stmt in enumerate(statements, 1):
            print(f"🔄 Translating Statement {i}:")
            print(f"   Input: {stmt}")
            
            result = engine.translate(stmt)
            if result.success:
                print("   ✅ Success")
                for line in result.python_code.split('\n'):
                    print(f"       {line}")
            else:
                print(f"   ❌ Failed: {result.error_message}")
            print()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_multiline_fix()
    test_single_line_multiple_statements()