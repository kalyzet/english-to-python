#!/usr/bin/env python3
"""
Demo script untuk menunjukkan data models bekerja dengan baik
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import ParsedSentence, Operation, Condition, PatternType, TranslationResult, ExecutionResult

def demo_parsed_sentence():
    """Demo ParsedSentence functionality"""
    print("=== ParsedSentence Demo ===")
    
    # Create a parsed sentence
    sentence = ParsedSentence(
        original_text="add x and y to get result",
        pattern_type=PatternType.ARITHMETIC
    )
    
    # Add variables
    sentence.add_variable("x", 5)
    sentence.add_variable("y", 3)
    
    # Add operation
    operation = Operation(
        operation_type="add",
        operands=["x", "y"],
        result_variable="result"
    )
    sentence.add_operation(operation)
    
    # Add condition
    condition = Condition(
        condition_text="x > 0",
        condition_type="if",
        variables_used=["x"]
    )
    sentence.add_condition(condition)
    
    print(f"Original text: {sentence.original_text}")
    print(f"Pattern type: {sentence.pattern_type.value}")
    print(f"Variables: {sentence.variables}")
    print(f"Operations: {len(sentence.operations)}")
    print(f"Conditions: {len(sentence.conditions)}")
    print(f"Is valid: {sentence.is_valid()}")
    print(f"Has arithmetic operations: {sentence.has_arithmetic_operations()}")
    
    # Test round-trip conversion
    data = sentence.to_dict()
    reconstructed = ParsedSentence.from_dict(data)
    print(f"Round-trip successful: {reconstructed.original_text == sentence.original_text}")
    print()

def demo_translation_result():
    """Demo TranslationResult functionality"""
    print("=== TranslationResult Demo ===")
    
    # Create successful translation
    success_result = TranslationResult.create_success(
        python_code="result = x + y",
        original_text="add x and y",
        translation_time=0.5
    )
    success_result.add_warning("Variable 'x' not defined in scope")
    
    print(f"Success: {success_result.success}")
    print(f"Python code: {success_result.python_code}")
    print(f"Warnings: {success_result.warnings}")
    print(f"Is executable: {success_result.is_executable()}")
    print(f"Summary: {success_result.get_summary()}")
    
    # Create error result
    error_result = TranslationResult.create_error(
        error_message="Could not parse input",
        original_text="invalid syntax here"
    )
    
    print(f"\nError result summary: {error_result.get_summary()}")
    print()

def demo_execution_result():
    """Demo ExecutionResult functionality"""
    print("=== ExecutionResult Demo ===")
    
    # Create execution result
    exec_result = ExecutionResult(
        success=True,
        output="8",
        execution_time=0.1,
        stdout="Calculation complete"
    )
    
    print(f"Success: {exec_result.success}")
    print(f"Output: {exec_result.output}")
    print(f"Has output: {exec_result.has_output()}")
    print(f"Combined output: {exec_result.get_combined_output()}")
    
    # Create translation with execution result
    translation = TranslationResult.create_success(
        python_code="print(5 + 3)",
        original_text="add 5 and 3"
    )
    translation.execution_result = exec_result
    
    print(f"\nTranslation with execution:")
    print(f"Summary: {translation.get_summary()}")
    print()

def main():
    """Main demo function"""
    print("English to Python Translator - Data Models Demo")
    print("=" * 50)
    
    try:
        demo_parsed_sentence()
        demo_translation_result()
        demo_execution_result()
        
        print("✓ All data models working correctly!")
        
    except Exception as e:
        print(f"✗ Error in demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())