#!/usr/bin/env python3
"""
Test script to demonstrate current conditional statement issues and improvements
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
except ImportError:
    # Try alternative import paths
    import src.core.input_parser as ip
    import src.core.code_generator as cg
    InputParser = ip.InputParser
    CodeGenerator = cg.CodeGenerator

def test_current_conditionals():
    """Test current conditional statement generation"""
    parser = InputParser()
    generator = CodeGenerator()
    
    test_cases = [
        "if age greater than 18 then print adult",
        "when temperature greater than 30 do print hot",
        "if score less than 60 then print fail else print pass",
    ]
    
    print("=== CURRENT CONDITIONAL GENERATION ===\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"Test {i}: {test_input}")
        print("-" * 50)
        
        try:
            # Parse the input
            parsed = parser.parse_sentence(test_input)
            print(f"Pattern Type: {parsed.pattern_type}")
            print(f"Conditions: {len(parsed.conditions)}")
            if parsed.conditions:
                print(f"Condition Text: {parsed.conditions[0].condition_text}")
            print(f"Metadata: {parsed.metadata}")
            
            # Generate code
            result = generator.generate(parsed)
            if result.success:
                print(f"Generated Code:\n{result.python_code}")
            else:
                print(f"Error: {result.error_message}")
                
        except Exception as e:
            print(f"Exception: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_current_conditionals()