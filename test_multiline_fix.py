#!/usr/bin/env python3
"""
Test fix untuk multiline input
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set test mode to avoid GUI
os.environ['PYTEST_CURRENT_TEST'] = 'true'

def test_multiline_fix():
    """Test fix untuk multiline input yang menyebabkan error"""
    
    try:
        from services.translation_engine import TranslationEngine
        from services.code_execution_service import CodeExecutionService
        
        engine = TranslationEngine()
        executor = CodeExecutionService()
        
        print("🔧 TEST: MULTILINE INPUT FIX")
        print("=" * 35)
        print()
        
        # Input yang sebelumnya menyebabkan error
        test_cases = [
            {
                "title": "Multiline Input (dengan newline)",
                "input": """set student_name to Alice
set math_score to 85
set english_score to 92
if math_score greater than 80 then print good_math else print poor_math
if english_score greater than 90 then print excellent_english else print good_english""",
                "expected_output": ["good_math", "excellent_english"]
            },
            {
                "title": "Single Line Multiple Statements",
                "input": "set age to 25set score to 85if age greater than 18 then print adult",
                "expected_output": ["adult"]
            },
            {
                "title": "Mixed Statements",
                "input": """set temperature to 35
when temperature greater than 30 do print hot
set humidity to 80
if humidity greater than 70 then print humid else print dry""",
                "expected_output": ["hot", "humid"]
            }
        ]
        
        for test_case in test_cases:
            print(f"🧪 {test_case['title']}")
            print("-" * 40)
            print("Input:")
            print(f"```\n{test_case['input']}\n```")
            print()
            
            # Test translation
            result = engine.translate(test_case['input'])
            
            if result.success:
                print("✅ Translation Success!")
                print("Generated Code:")
                print("```python")
                print(result.python_code)
                print("```")
                
                # Show warnings if any
                if result.has_warnings():
                    print("⚠️  Warnings:")
                    for warning in result.warnings:
                        print(f"    {warning}")
                
                # Test execution
                print("\n▶️  Executing...")
                exec_result = executor.execute_code(result.python_code)
                
                if exec_result.success:
                    print("✅ Execution Success!")
                    if exec_result.has_output():
                        output_lines = exec_result.get_combined_output().strip().split('\n')
                        print("📤 Output:")
                        for line in output_lines:
                            print(f"    {line}")
                        
                        # Check expected output
                        expected = test_case['expected_output']
                        if all(exp in output_lines for exp in expected):
                            print("✅ Output matches expected!")
                        else:
                            print(f"⚠️  Expected: {expected}")
                            print(f"⚠️  Got: {output_lines}")
                    else:
                        print("ℹ️  No output produced")
                else:
                    print("❌ Execution Failed!")
                    print(f"Error: {exec_result.get_combined_error()}")
                    
            else:
                print("❌ Translation Failed!")
                print(f"Error: {result.error_message}")
            
            print()
            print("=" * 50)
            print()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_edge_cases():
    """Test edge cases untuk multiline handling"""
    
    try:
        from services.translation_engine import TranslationEngine
        
        engine = TranslationEngine()
        
        print("🧪 TEST: EDGE CASES")
        print("=" * 25)
        print()
        
        edge_cases = [
            {
                "title": "Empty lines in between",
                "input": """set x to 10

set y to 20

if x greater than 5 then print yes"""
            },
            {
                "title": "Single statement (should work normally)",
                "input": "set age to 25"
            },
            {
                "title": "Complex conditional with multiple statements",
                "input": """set score to 85
set grade to A
if score greater than 80 then print excellent else print good
when grade equals A do print top_grade"""
            }
        ]
        
        for case in edge_cases:
            print(f"🔍 {case['title']}")
            print(f"Input: {repr(case['input'])}")
            print("-" * 30)
            
            result = engine.translate(case['input'])
            
            if result.success:
                print("✅ Success!")
                print("Generated:")
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
                    
                if result.has_warnings():
                    print("Warnings:")
                    for warning in result.warnings:
                        print(f"    {warning}")
            else:
                print("❌ Failed!")
                print(f"Error: {result.error_message}")
            
            print()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_multiline_fix()
    test_edge_cases()