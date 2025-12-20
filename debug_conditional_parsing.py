#!/usr/bin/env python3
"""
Debug script to understand conditional parsing issues
"""

import sys
import os
import re

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from core.input_parser import InputParser
except ImportError:
    import src.core.input_parser as ip
    InputParser = ip.InputParser

def debug_conditional_patterns():
    """Debug conditional pattern matching"""
    parser = InputParser()
    
    test_cases = [
        "if age greater than 18 then print adult",
        "when temperature greater than 30 do print hot",
        "if score less than 60 then print fail else print pass",
    ]
    
    print("=== DEBUGGING CONDITIONAL PATTERNS ===\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"Test {i}: {test_input}")
        print("-" * 50)
        
        # Test pattern matching directly
        match_result = parser.pattern_matcher.match_conditional(test_input)
        if match_result:
            condition_type, parts = match_result
            print(f"Match found: {condition_type}")
            print(f"Parts: {parts}")
            for j, part in enumerate(parts):
                print(f"  Part {j}: '{part}'")
        else:
            print("No match found")
        
        print("\n" + "="*60 + "\n")

def test_format_action():
    """Test the _format_action method"""
    parser = InputParser()
    
    test_actions = [
        "print adult",
        "print hot", 
        "print fail",
        "print pass",
        "set x to 5"
    ]
    
    print("=== TESTING _format_action METHOD ===\n")
    
    for action in test_actions:
        try:
            formatted = parser._format_action(action)
            print(f"'{action}' -> '{formatted}'")
        except Exception as e:
            print(f"'{action}' -> ERROR: {e}")
    
    print()

if __name__ == "__main__":
    debug_conditional_patterns()
    test_format_action()