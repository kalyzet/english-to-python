#!/usr/bin/env python3
"""
Demo script showing the improved conditional statement functionality
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from core.input_parser import InputParser
    from core.code_generator import CodeGenerator
    from services.translation_engine import TranslationEngine
except ImportError:
    print("Import error - running from main.py instead")
    sys.exit(1)

def demo_improved_conditionals():
    """Demonstrate the improved conditional statement functionality"""
    engine = TranslationEngine()
    
    print("🎉 IMPROVED CONDITIONAL STATEMENTS DEMO")
    print("=" * 50)
    print()
    
    # Test cases showing the improvements
    test_cases = [
        {
            "title": "✅ Basic IF-THEN with Print Statement",
            "input": "if age greater than 18 then print adult",
            "description": "Now generates actual print() calls instead of 'pass'"
        },
        {
            "title": "✅ WHEN-DO Pattern Support", 
            "input": "when temperature greater than 30 do print hot",
            "description": "Alternative conditional syntax works correctly"
        },
        {
            "title": "✅ IF-THEN-ELSE with Print Statements",
            "input": "if score less than 60 then print fail else print pass", 
            "description": "Else clauses now work with proper print statements"
        },
        {
            "title": "✅ Variable vs String Detection",
            "input": "if status equals active then print running",
            "description": "Detects when to print variables vs string literals"
        },
        {
            "title": "✅ Complex Conditions",
            "input": "if count equals 0 then print empty else print found",
            "description": "Handles complex conditional logic properly"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['title']}")
        print(f"   Input: {test_case['input']}")
        print(f"   {test_case['description']}")
        print()
        
        try:
            result = engine.translate(test_case['input'])
            if result.success:
                print("   Generated Python Code:")
                for line in result.python_code.split('\n'):
                    print(f"   {line}")
                print()
            else:
                print(f"   ❌ Error: {result.error_message}")
                print()
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            print()
        
        print("-" * 50)
        print()

def demo_complete_workflow():
    """Demo a complete workflow with variable setup and conditionals"""
    engine = TranslationEngine()
    
    print("🚀 COMPLETE WORKFLOW DEMO")
    print("=" * 30)
    print()
    
    workflow_steps = [
        "set age to 20",
        "set score to 85", 
        "set temperature to 35",
        "if age greater than 18 then print adult",
        "if score greater than 80 then print excellent else print good",
        "when temperature greater than 30 do print hot"
    ]
    
    print("Workflow Steps:")
    for i, step in enumerate(workflow_steps, 1):
        print(f"{i}. {step}")
    print()
    
    print("Generated Python Code:")
    print("-" * 20)
    
    all_code = []
    for step in workflow_steps:
        try:
            result = engine.translate(step)
            if result.success:
                all_code.append(result.python_code)
            else:
                all_code.append(f"# Error: {result.error_message}")
        except Exception as e:
            all_code.append(f"# Exception: {e}")
    
    final_code = '\n'.join(all_code)
    print(final_code)
    print()
    
    print("Expected Output when run:")
    print("adult")
    print("excellent") 
    print("hot")

if __name__ == "__main__":
    demo_improved_conditionals()
    demo_complete_workflow()