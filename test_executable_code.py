#!/usr/bin/env python3
"""
Test untuk memastikan kode yang dihasilkan bisa dieksekusi dengan benar
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set test mode to avoid GUI
os.environ['PYTEST_CURRENT_TEST'] = 'true'

def test_executable_conditional_code():
    """Test bahwa kode conditional yang dihasilkan bisa dieksekusi"""
    
    try:
        from services.translation_engine import TranslationEngine
        from services.code_execution_service import CodeExecutionService
        
        engine = TranslationEngine()
        executor = CodeExecutionService()
        
        print("🧪 TEST: KODE CONDITIONAL YANG BISA DIEKSEKUSI")
        print("=" * 55)
        print()
        
        test_cases = [
            {
                "title": "IF-THEN dengan Print String",
                "setup": ["set age to 25"],
                "input": "if age greater than 18 then print adult",
                "expected_output": "adult"
            },
            {
                "title": "IF-THEN-ELSE dengan Print String",
                "setup": ["set score to 85"],
                "input": "if score greater than 90 then print excellent else print good",
                "expected_output": "good"
            },
            {
                "title": "WHEN-DO Pattern",
                "setup": ["set temperature to 35"],
                "input": "when temperature greater than 30 do print hot",
                "expected_output": "hot"
            },
            {
                "title": "Multiple Conditions",
                "setup": ["set age to 20", "set status to active"],
                "input": "if age equals 20 then print twenty",
                "expected_output": "twenty"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case['title']}")
            print(f"Input: {test_case['input']}")
            print("-" * 50)
            
            # Setup variables first
            setup_code = []
            for setup_input in test_case['setup']:
                setup_result = engine.translate(setup_input)
                if setup_result.success:
                    setup_code.append(setup_result.python_code)
                else:
                    print(f"❌ Setup failed: {setup_result.error_message}")
                    continue
            
            # Translate main input
            result = engine.translate(test_case['input'])
            
            if result.success:
                print("✅ Translation Success!")
                print("Generated Code:")
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
                
                # Combine setup and main code
                full_code = '\n'.join(setup_code) + '\n' + result.python_code
                print()
                print("Full Code to Execute:")
                for line in full_code.split('\n'):
                    print(f"    {line}")
                
                # Execute the code
                print()
                print("Executing...")
                exec_result = executor.execute_code(full_code)
                
                if exec_result.success:
                    print("✅ Execution Success!")
                    if exec_result.has_output():
                        print(f"Output: {exec_result.get_combined_output()}")
                        
                        # Check if output matches expected
                        if test_case['expected_output'] in exec_result.get_combined_output():
                            print("✅ Output matches expected!")
                        else:
                            print(f"⚠️  Expected '{test_case['expected_output']}' but got '{exec_result.get_combined_output()}'")
                    else:
                        print("ℹ️  No output produced")
                else:
                    print("❌ Execution Failed!")
                    print(f"Error: {exec_result.get_combined_error()}")
                    
            else:
                print("❌ Translation Failed!")
                print(f"Error: {result.error_message}")
            
            print()
            print("=" * 55)
            print()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_workflow_execution():
    """Test workflow lengkap yang bisa dieksekusi"""
    
    try:
        from services.translation_engine import TranslationEngine
        from services.code_execution_service import CodeExecutionService
        
        engine = TranslationEngine()
        executor = CodeExecutionService()
        
        print("🚀 TEST: WORKFLOW LENGKAP YANG BISA DIEKSEKUSI")
        print("=" * 50)
        print()
        
        workflow = [
            "set age to 20",
            "set score to 85",
            "if age greater than 18 then print adult",
            "if score greater than 80 then print excellent else print good"
        ]
        
        print("📋 WORKFLOW:")
        for i, step in enumerate(workflow, 1):
            print(f"{i}. {step}")
        print()
        
        all_code = []
        
        print("🔄 TRANSLATING EACH STEP:")
        print("-" * 30)
        
        for i, step in enumerate(workflow, 1):
            print(f"Step {i}: {step}")
            
            result = engine.translate(step)
            if result.success:
                print("✅ Success")
                all_code.append(result.python_code)
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
            else:
                print(f"❌ Failed: {result.error_message}")
            
            print()
        
        # Execute complete workflow
        final_code = '\n'.join(all_code)
        
        print("🎯 FINAL CODE:")
        print("-" * 20)
        print(final_code)
        print()
        
        print("▶️  EXECUTING WORKFLOW...")
        exec_result = executor.execute_code(final_code)
        
        if exec_result.success:
            print("✅ WORKFLOW EXECUTION SUCCESS!")
            if exec_result.has_output():
                print("📤 OUTPUT:")
                print(exec_result.get_combined_output())
            else:
                print("ℹ️  No output produced")
        else:
            print("❌ WORKFLOW EXECUTION FAILED!")
            print(f"Error: {exec_result.get_combined_error()}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_executable_conditional_code()
    test_workflow_execution()