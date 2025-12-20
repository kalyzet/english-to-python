#!/usr/bin/env python3
"""
Test untuk memperbaiki assignment dengan string values
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set test mode to avoid GUI
os.environ['PYTEST_CURRENT_TEST'] = 'true'

def test_assignment_string_handling():
    """Test assignment dengan string values"""
    
    try:
        from services.translation_engine import TranslationEngine
        from services.code_execution_service import CodeExecutionService
        
        engine = TranslationEngine()
        executor = CodeExecutionService()
        
        print("🧪 TEST: ASSIGNMENT STRING HANDLING")
        print("=" * 40)
        print()
        
        test_cases = [
            {
                "input": "set status to active",
                "expected_code": 'status = "active"',
                "description": "String value should be quoted"
            },
            {
                "input": "set age to 25",
                "expected_code": "age = 25",
                "description": "Number should not be quoted"
            },
            {
                "input": "set is_member to true",
                "expected_code": "is_member = True",
                "description": "Boolean should be capitalized"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case['description']}")
            print(f"Input: {test_case['input']}")
            print(f"Expected: {test_case['expected_code']}")
            print("-" * 40)
            
            result = engine.translate(test_case['input'])
            
            if result.success:
                print("✅ Translation Success!")
                print(f"Generated: {result.python_code}")
                
                # Test execution
                exec_result = executor.execute_code(result.python_code)
                if exec_result.success:
                    print("✅ Execution Success!")
                else:
                    print("❌ Execution Failed!")
                    print(f"Error: {exec_result.get_combined_error()}")
                    
            else:
                print("❌ Translation Failed!")
                print(f"Error: {result.error_message}")
            
            print()
            print("=" * 40)
            print()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_assignment_string_handling()