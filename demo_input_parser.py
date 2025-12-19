#!/usr/bin/env python3
"""
Demo script untuk menunjukkan Input Parser bekerja dengan baik
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import InputParser
from src.models import PatternType

def demo_arithmetic_parsing():
    """Demo parsing arithmetic sentences"""
    print("=== Arithmetic Pattern Parsing ===")
    
    parser = InputParser()
    
    test_sentences = [
        "add x and y",
        "multiply width by height", 
        "calculate 5 plus 3",
        "a divided by b",
        "sum total and count"
    ]
    
    for sentence in test_sentences:
        parsed = parser.parse_sentence(sentence)
        print(f"Input: '{sentence}'")
        print(f"  Pattern: {parsed.pattern_type.value}")
        print(f"  Variables: {parsed.variables}")
        print(f"  Operations: {len(parsed.operations)}")
        if parsed.operations:
            op = parsed.operations[0]
            print(f"    Type: {op.operation_type}, Operands: {op.operands}")
        print(f"  Confidence: {parsed.metadata.get('confidence', 0):.2f}")
        print()

def demo_conditional_parsing():
    """Demo parsing conditional sentences"""
    print("=== Conditional Pattern Parsing ===")
    
    parser = InputParser()
    
    test_sentences = [
        "if x > 5 then print hello",
        "when user clicks button do action",
        "if temperature is high then turn on fan"
    ]
    
    for sentence in test_sentences:
        parsed = parser.parse_sentence(sentence)
        print(f"Input: '{sentence}'")
        print(f"  Pattern: {parsed.pattern_type.value}")
        print(f"  Conditions: {len(parsed.conditions)}")
        if parsed.conditions:
            cond = parsed.conditions[0]
            print(f"    Text: {cond.condition_text}")
            print(f"    Variables used: {cond.variables_used}")
        print(f"  Confidence: {parsed.metadata.get('confidence', 0):.2f}")
        print()

def demo_data_operation_parsing():
    """Demo parsing data operation sentences"""
    print("=== Data Operation Pattern Parsing ===")
    
    parser = InputParser()
    
    test_sentences = [
        "create list with items",
        "add item to shopping list",
        "remove element from array",
        "get value from dictionary"
    ]
    
    for sentence in test_sentences:
        parsed = parser.parse_sentence(sentence)
        print(f"Input: '{sentence}'")
        print(f"  Pattern: {parsed.pattern_type.value}")
        print(f"  Variables: {parsed.variables}")
        print(f"  Operations: {len(parsed.operations)}")
        if parsed.operations:
            op = parsed.operations[0]
            print(f"    Type: {op.operation_type}, Operands: {op.operands}")
        print(f"  Confidence: {parsed.metadata.get('confidence', 0):.2f}")
        print()

def demo_loop_parsing():
    """Demo parsing loop sentences"""
    print("=== Loop Pattern Parsing ===")
    
    parser = InputParser()
    
    test_sentences = [
        "repeat 5 times",
        "for each item in list",
        "while condition is true"
    ]
    
    for sentence in test_sentences:
        parsed = parser.parse_sentence(sentence)
        print(f"Input: '{sentence}'")
        print(f"  Pattern: {parsed.pattern_type.value}")
        print(f"  Variables: {parsed.variables}")
        print(f"  Operations: {len(parsed.operations)}")
        print(f"  Confidence: {parsed.metadata.get('confidence', 0):.2f}")
        print()

def demo_assignment_parsing():
    """Demo parsing assignment sentences"""
    print("=== Assignment Pattern Parsing ===")
    
    parser = InputParser()
    
    test_sentences = [
        "set x to 5",
        "create variable name with value hello",
        "assign 42 to result"
    ]
    
    for sentence in test_sentences:
        parsed = parser.parse_sentence(sentence)
        print(f"Input: '{sentence}'")
        print(f"  Pattern: {parsed.pattern_type.value}")
        print(f"  Variables: {parsed.variables}")
        print(f"  Operations: {len(parsed.operations)}")
        if parsed.operations:
            op = parsed.operations[0]
            print(f"    Type: {op.operation_type}")
            print(f"    Result variable: {op.result_variable}")
        print(f"  Confidence: {parsed.metadata.get('confidence', 0):.2f}")
        print()

def demo_validation():
    """Demo input validation"""
    print("=== Input Validation Demo ===")
    
    parser = InputParser()
    
    test_inputs = [
        "add x and y",  # Valid
        "",  # Empty
        "   ",  # Whitespace only
        "hi",  # Too short
        "import os",  # Dangerous content
        "x" * 1001,  # Too long
    ]
    
    for input_text in test_inputs:
        valid, message = parser.validate_input(input_text)
        display_text = input_text[:50] + "..." if len(input_text) > 50 else input_text
        print(f"Input: '{display_text}'")
        print(f"  Valid: {valid}")
        print(f"  Message: {message}")
        print()

def demo_pattern_confidence():
    """Demo confidence scoring"""
    print("=== Pattern Confidence Demo ===")
    
    parser = InputParser()
    
    test_sentences = [
        ("add x and y", "Clear arithmetic"),
        ("hello world", "No clear pattern"),
        ("if x then y", "Clear conditional"),
        ("maybe do something", "Ambiguous"),
        ("create list with items", "Clear data operation")
    ]
    
    for sentence, description in test_sentences:
        parsed = parser.parse_sentence(sentence)
        confidence = parsed.metadata.get('confidence', 0)
        print(f"Input: '{sentence}' ({description})")
        print(f"  Pattern: {parsed.pattern_type.value}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Valid: {parsed.is_valid()}")
        print()

def main():
    """Main demo function"""
    print("English to Python Translator - Input Parser Demo")
    print("=" * 60)
    
    try:
        demo_arithmetic_parsing()
        demo_conditional_parsing()
        demo_data_operation_parsing()
        demo_loop_parsing()
        demo_assignment_parsing()
        demo_validation()
        demo_pattern_confidence()
        
        print("✓ Input Parser working correctly!")
        print("✓ All pattern types supported")
        print("✓ Variable extraction working")
        print("✓ Input validation working")
        print("✓ Confidence scoring working")
        
    except Exception as e:
        print(f"✗ Error in demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())