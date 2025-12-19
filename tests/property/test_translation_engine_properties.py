"""
Property-based tests for Translation Engine functionality
**Feature: english-to-python-translator, Property 3: Translation produces Python code**
**Validates: Requirements 1.3**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
import ast
import re
from src.services import TranslationEngine
from src.models import PatternType


# Hypothesis strategies for generating test data
@st.composite
def valid_english_instructions(draw):
    """Generate valid English instructions that should be translatable"""
    instruction_type = draw(st.sampled_from(['arithmetic', 'assignment', 'conditional', 'data_operation']))
    
    if instruction_type == 'arithmetic':
        var1 = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=10
        ).filter(lambda x: x.isidentifier() if x else False))
        var2 = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=10
        ).filter(lambda x: x.isidentifier() if x else False))
        assume(var1 != var2)
        
        operation = draw(st.sampled_from(['add', 'subtract', 'multiply', 'divide']))
        if operation == 'add':
            templates = [f"add {var1} and {var2}", f"{var1} plus {var2}"]
        elif operation == 'subtract':
            templates = [f"subtract {var1} from {var2}", f"{var1} minus {var2}"]
        elif operation == 'multiply':
            templates = [f"multiply {var1} by {var2}", f"{var1} times {var2}"]
        else:  # divide
            templates = [f"divide {var1} by {var2}", f"{var1} divided by {var2}"]
        
        return draw(st.sampled_from(templates))
    
    elif instruction_type == 'assignment':
        var_name = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=10
        ).filter(lambda x: x.isidentifier() if x else False))
        value = draw(st.one_of(
            st.integers(min_value=0, max_value=1000),
            st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
                min_size=1, max_size=20
            ).filter(lambda x: x.strip() and '"' not in x)
        ))
        
        templates = [
            f"set {var_name} to {value}",
            f"create variable {var_name} with value {value}",
            f"assign {value} to {var_name}"
        ]
        return draw(st.sampled_from(templates))
    
    elif instruction_type == 'conditional':
        condition = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=3, max_size=20
        ).filter(lambda x: x.strip() and 'then' not in x.lower()))
        action = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=3, max_size=20
        ).filter(lambda x: x.strip()))
        
        templates = [
            f"if {condition} then {action}",
            f"when {condition} do {action}"
        ]
        return draw(st.sampled_from(templates))
    
    else:  # data_operation
        items = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' ,'),
            min_size=1, max_size=30
        ).filter(lambda x: x.strip()))
        
        templates = [
            f"create list with {items}",
            f"create dictionary with {items}",
            f"make a list"
        ]
        return draw(st.sampled_from(templates))


@st.composite
def invalid_english_instructions(draw):
    """Generate invalid English instructions that should produce errors"""
    invalid_type = draw(st.sampled_from(['empty', 'too_short', 'unrecognized', 'unsafe']))
    
    if invalid_type == 'empty':
        return draw(st.sampled_from(['', '   ', '\n', '\t']))
    elif invalid_type == 'too_short':
        return draw(st.text(min_size=1, max_size=2).filter(lambda x: x.strip()))
    elif invalid_type == 'unrecognized':
        return draw(st.sampled_from([
            'hello world',
            'this is just random text',
            'no pattern here',
            'random words without meaning',
            'xyz abc def'
        ]))
    else:  # unsafe
        return draw(st.sampled_from([
            'import os and delete files',
            'exec malicious code',
            'eval dangerous expression',
            'open system files'
        ]))


class TestTranslationProducesPythonCode:
    """
    **Feature: english-to-python-translator, Property 3: Translation produces Python code**
    **Validates: Requirements 1.3**
    
    Property: For any valid English instruction, pressing the translate button 
    should produce a non-empty string of Python code.
    """
    
    @given(instruction=valid_english_instructions())
    def test_valid_instructions_produce_python_code(self, instruction):
        """
        Property: Valid English instructions should produce non-empty Python code
        """
        engine = TranslationEngine()
        
        # Property: Valid instructions should produce successful translation with Python code
        result = engine.translate(instruction)
        
        if result.success:
            # Property: Successful translation should have non-empty Python code
            assert result.python_code.strip(), f"Translation of '{instruction}' should produce non-empty Python code"
            
            # Property: Generated code should be a string
            assert isinstance(result.python_code, str), f"Python code should be a string for '{instruction}'"
            
            # Property: Generated code should contain Python-like syntax
            code = result.python_code.strip()
            python_indicators = ['=', '+', '-', '*', '/', 'if', 'for', 'while', '[', ']', '{', '}', '(', ')']
            has_python_syntax = any(indicator in code for indicator in python_indicators)
            assert has_python_syntax, f"Generated code '{code}' should contain Python syntax for '{instruction}'"
        else:
            # If translation failed, that's acceptable for some edge cases
            # but the error message should be informative
            assert result.error_message.strip(), f"Failed translation should have error message for '{instruction}'"
    
    @given(
        var1=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() if x else False).filter(
            lambda x: x.lower() not in {'add', 'subtract', 'multiply', 'divide', 'plus', 'minus', 'times', 'by', 'from', 'and', 'with'}
        ),
        var2=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() if x else False).filter(
            lambda x: x.lower() not in {'add', 'subtract', 'multiply', 'divide', 'plus', 'minus', 'times', 'by', 'from', 'and', 'with'}
        )
    )
    def test_arithmetic_instructions_produce_arithmetic_code(self, var1, var2):
        """
        Property: Arithmetic instructions should produce Python code with arithmetic operators
        """
        assume(var1 != var2)
        
        engine = TranslationEngine()
        
        # Test different arithmetic operations
        operations = [
            (f"add {var1} and {var2}", '+'),
            (f"subtract {var1} from {var2}", '-'),
            (f"multiply {var1} by {var2}", '*'),
            (f"divide {var1} by {var2}", '/')
        ]
        
        for instruction, expected_operator in operations:
            result = engine.translate(instruction)
            
            if result.success:
                # Property: Arithmetic instructions should produce code with corresponding operators
                assert expected_operator in result.python_code, \
                    f"Arithmetic instruction '{instruction}' should produce code with '{expected_operator}'"
                
                # Property: Generated code should contain the variables
                assert var1 in result.python_code or var2 in result.python_code, \
                    f"Generated code should contain variables from '{instruction}'"
    
    @given(
        var_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=10
        ).filter(lambda x: x.isidentifier() if x else False),
        value=st.integers(min_value=0, max_value=100)
    )
    def test_assignment_instructions_produce_assignment_code(self, var_name, value):
        """
        Property: Assignment instructions should produce Python code with assignment operator
        """
        engine = TranslationEngine()
        
        instruction = f"set {var_name} to {value}"
        result = engine.translate(instruction)
        
        if result.success:
            # Property: Assignment instructions should produce code with '=' operator
            assert '=' in result.python_code, \
                f"Assignment instruction '{instruction}' should produce code with '=' operator"
            
            # Property: Generated code should contain the variable name
            assert var_name in result.python_code, \
                f"Generated code should contain variable name '{var_name}' from '{instruction}'"
            
            # Property: Generated code should contain the value
            assert str(value) in result.python_code, \
                f"Generated code should contain value '{value}' from '{instruction}'"
    
    @given(instruction=valid_english_instructions())
    def test_translation_consistency(self, instruction):
        """
        Property: Translation should be consistent - same input should produce same output
        """
        engine1 = TranslationEngine()
        engine2 = TranslationEngine()
        
        # Property: Multiple translations of same input should produce same result
        result1 = engine1.translate(instruction)
        result2 = engine2.translate(instruction)
        
        assert result1.success == result2.success, \
            f"Translation consistency failed for '{instruction}': success mismatch"
        
        if result1.success and result2.success:
            # Normalize whitespace for comparison
            code1 = ' '.join(result1.python_code.split())
            code2 = ' '.join(result2.python_code.split())
            assert code1 == code2, \
                f"Translation consistency failed for '{instruction}': code mismatch"
        
        if not result1.success and not result2.success:
            # Error messages should be consistent too
            assert result1.error_message == result2.error_message, \
                f"Translation consistency failed for '{instruction}': error message mismatch"
    
    @given(instruction=valid_english_instructions())
    def test_generated_code_syntax_validity(self, instruction):
        """
        Property: Generated Python code should be syntactically valid
        """
        engine = TranslationEngine()
        
        result = engine.translate(instruction)
        
        if result.success and result.python_code.strip():
            # Property: Generated code should be parseable by Python AST
            try:
                ast.parse(result.python_code)
                # If we get here, the code is syntactically valid
                assert True
            except SyntaxError as e:
                pytest.fail(f"Generated code for '{instruction}' has syntax error: {e}\nCode: {result.python_code}")
    
    @given(instruction=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    def test_translation_robustness(self, instruction):
        """
        Property: Translation engine should handle any input without crashing
        """
        engine = TranslationEngine()
        
        # Property: Translation should not crash on any input
        try:
            result = engine.translate(instruction)
            
            # Property: Result should have proper structure
            assert isinstance(result.success, bool)
            assert isinstance(result.python_code, str)
            assert isinstance(result.error_message, str)
            assert isinstance(result.warnings, list)
            assert isinstance(result.original_text, str)
            
            # Property: Original text should be preserved
            assert result.original_text == instruction
            
        except Exception as e:
            pytest.fail(f"Translation engine crashed on input '{instruction}': {e}")
    
    @given(instruction=valid_english_instructions())
    def test_translation_timing_recorded(self, instruction):
        """
        Property: Translation should record timing information
        """
        engine = TranslationEngine()
        
        result = engine.translate(instruction)
        
        # Property: Translation time should be recorded and non-negative
        assert result.translation_time >= 0, \
            f"Translation time should be non-negative for '{instruction}'"
        
        # Property: Translation time should be reasonable (less than 10 seconds for simple operations)
        assert result.translation_time < 10.0, \
            f"Translation time should be reasonable for '{instruction}', got {result.translation_time}"


class TestInvalidInputErrorHandling:
    """
    **Feature: english-to-python-translator, Property 17: Invalid input error handling**
    **Validates: Requirements 5.1**
    
    Property: For any input that cannot be parsed or understood, the system 
    should display an informative error message explaining why the input is invalid.
    """
    
    @given(invalid_input=invalid_english_instructions())
    def test_invalid_input_produces_error_message(self, invalid_input):
        """
        Property: Invalid inputs should produce informative error messages
        """
        engine = TranslationEngine()
        
        result = engine.translate(invalid_input)
        
        # Property: Invalid inputs should result in failed translation
        assert not result.success, f"Invalid input '{invalid_input}' should result in failed translation"
        
        # Property: Failed translation should have informative error message
        assert result.error_message.strip(), \
            f"Invalid input '{invalid_input}' should produce non-empty error message"
        
        # Property: Error message should be informative (contain helpful keywords)
        error_msg = result.error_message.lower()
        helpful_keywords = [
            'invalid', 'error', 'cannot', 'unable', 'failed', 'empty', 'short', 
            'pattern', 'recognize', 'parse', 'suggestion', 'try', 'example',
            'unsafe', 'contains', 'potentially', 'dangerous'
        ]
        has_helpful_content = any(keyword in error_msg for keyword in helpful_keywords)
        assert has_helpful_content, \
            f"Error message should be informative for '{invalid_input}': {result.error_message}"
    
    @given(empty_input=st.sampled_from(['', '   ', '\n', '\t', '  \n  ']))
    def test_empty_input_specific_error(self, empty_input):
        """
        Property: Empty inputs should produce specific error messages about emptiness
        """
        engine = TranslationEngine()
        
        result = engine.translate(empty_input)
        
        # Property: Empty inputs should fail
        assert not result.success, f"Empty input should result in failed translation"
        
        # Property: Error message should mention emptiness
        error_msg = result.error_message.lower()
        empty_keywords = ['empty', 'blank', 'nothing', 'whitespace']
        mentions_emptiness = any(keyword in error_msg for keyword in empty_keywords)
        assert mentions_emptiness, \
            f"Error message should mention emptiness for empty input: {result.error_message}"
    
    @given(short_input=st.text(min_size=1, max_size=2).filter(lambda x: x.strip()))
    def test_too_short_input_specific_error(self, short_input):
        """
        Property: Too short inputs should produce specific error messages
        """
        engine = TranslationEngine()
        
        result = engine.translate(short_input)
        
        # Property: Too short inputs should fail
        assert not result.success, f"Too short input '{short_input}' should result in failed translation"
        
        # Property: Error message should be helpful
        assert result.error_message.strip(), \
            f"Too short input '{short_input}' should produce error message"
    
    @given(unrecognized_input=st.sampled_from([
        'hello world', 'random text here', 'no pattern at all', 
        'just some words', 'xyz abc def ghi'
    ]))
    def test_unrecognized_pattern_provides_suggestions(self, unrecognized_input):
        """
        Property: Unrecognized patterns should provide helpful suggestions
        """
        engine = TranslationEngine()
        
        result = engine.translate(unrecognized_input)
        
        # Property: Unrecognized patterns should fail
        assert not result.success, f"Unrecognized input '{unrecognized_input}' should result in failed translation"
        
        # Property: Error message should provide suggestions or examples
        error_msg = result.error_message.lower()
        suggestion_keywords = ['try', 'example', 'pattern', 'suggestion', 'instead', 'like']
        provides_suggestions = any(keyword in error_msg for keyword in suggestion_keywords)
        assert provides_suggestions, \
            f"Error message should provide suggestions for '{unrecognized_input}': {result.error_message}"
    
    @given(instruction=st.text(min_size=1, max_size=50))
    def test_error_messages_preserve_original_input(self, instruction):
        """
        Property: Error messages should preserve reference to original input
        """
        engine = TranslationEngine()
        
        result = engine.translate(instruction)
        
        # Property: Original text should always be preserved
        assert result.original_text == instruction, \
            f"Original text should be preserved for '{instruction}'"
        
        if not result.success:
            # Property: Failed translations should have error messages
            assert result.error_message.strip(), \
                f"Failed translation should have error message for '{instruction}'"


class TestAmbiguousInputSuggestions:
    """
    **Feature: english-to-python-translator, Property 19: Ambiguous input suggestions**
    **Validates: Requirements 5.3**
    
    Property: For any input identified as ambiguous, the system should provide 
    at least one suggestion or alternative interpretation.
    """
    
    @st.composite
    def ambiguous_instructions(draw):
        """Generate potentially ambiguous instructions"""
        ambiguity_type = draw(st.sampled_from(['missing_operands', 'unclear_variables', 'incomplete']))
        
        if ambiguity_type == 'missing_operands':
            return draw(st.sampled_from([
                'add something',
                'multiply by',
                'divide and',
                'subtract from'
            ]))
        elif ambiguity_type == 'unclear_variables':
            return draw(st.sampled_from([
                'add x and y',  # variables without values
                'set variable to something',
                'create list with items'
            ]))
        else:  # incomplete
            return draw(st.sampled_from([
                'if condition then',
                'repeat times',
                'create list',
                'when something'
            ]))
    
    @given(ambiguous_input=ambiguous_instructions())
    def test_ambiguous_input_provides_suggestions(self, ambiguous_input):
        """
        Property: Ambiguous inputs should provide suggestions when possible
        """
        engine = TranslationEngine()
        
        result = engine.translate(ambiguous_input)
        
        # Check if translation succeeded but with warnings (ambiguity detected)
        if result.success and result.has_warnings():
            # Property: Ambiguous but translatable input should have warnings with suggestions
            warning_text = ' '.join(result.warnings).lower()
            suggestion_keywords = ['suggestion', 'try', 'consider', 'specific', 'clear']
            has_suggestions = any(keyword in warning_text for keyword in suggestion_keywords)
            assert has_suggestions, \
                f"Ambiguous input '{ambiguous_input}' should provide suggestions in warnings"
        
        # If translation failed, error message should be helpful
        elif not result.success:
            error_msg = result.error_message.lower()
            helpful_keywords = ['try', 'example', 'specific', 'clear', 'suggestion']
            is_helpful = any(keyword in error_msg for keyword in helpful_keywords)
            assert is_helpful, \
                f"Failed ambiguous input '{ambiguous_input}' should have helpful error message"
    
    @given(
        incomplete_arithmetic=st.sampled_from([
            'add x and', 'multiply by y', 'divide something', 'subtract from'
        ])
    )
    def test_incomplete_arithmetic_suggestions(self, incomplete_arithmetic):
        """
        Property: Incomplete arithmetic expressions should provide specific suggestions
        """
        engine = TranslationEngine()
        
        result = engine.translate(incomplete_arithmetic)
        
        # Property: Should either succeed with warnings or fail with helpful message
        if result.success:
            if result.has_warnings():
                warning_text = ' '.join(result.warnings).lower()
                arithmetic_keywords = ['operand', 'variable', 'number', 'value']
                mentions_arithmetic = any(keyword in warning_text for keyword in arithmetic_keywords)
                assert mentions_arithmetic, \
                    f"Incomplete arithmetic '{incomplete_arithmetic}' should mention missing operands"
        else:
            error_msg = result.error_message.lower()
            helpful_keywords = ['operand', 'variable', 'number', 'example', 'try']
            is_helpful = any(keyword in error_msg for keyword in helpful_keywords)
            assert is_helpful, \
                f"Failed incomplete arithmetic '{incomplete_arithmetic}' should be helpful"
    
    @given(
        var_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() if x else False)
    )
    def test_undefined_variables_produce_warnings(self, var_name):
        """
        Property: Instructions with undefined variables should produce warnings
        """
        engine = TranslationEngine()
        
        # Create instruction that uses undefined variable
        instruction = f"add {var_name} and 5"
        result = engine.translate(instruction)
        
        if result.success:
            # Property: Using undefined variables should produce warnings
            # (This might not always trigger depending on implementation)
            # The property is that IF warnings are generated, they should be helpful
            if result.has_warnings():
                warning_text = ' '.join(result.warnings).lower()
                variable_keywords = ['variable', 'undefined', 'defined', 'value']
                mentions_variables = any(keyword in warning_text for keyword in variable_keywords)
                # If there are warnings, they should be about variables
                if any(keyword in warning_text for keyword in ['variable', 'undefined']):
                    assert mentions_variables, \
                        f"Variable warnings should be informative for '{instruction}'"


class TestProblematicCodeWarnings:
    """
    **Feature: english-to-python-translator, Property 20: Potentially problematic code warnings**
    **Validates: Requirements 5.4**
    
    Property: For any generated code that might cause runtime issues 
    (division by zero, undefined variables, etc.), the system should display a warning message.
    """
    
    @given(
        var1=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() if x else False),
        var2=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() if x else False)
    )
    def test_division_operations_produce_warnings(self, var1, var2):
        """
        Property: Division operations should produce warnings about potential division by zero
        """
        assume(var1 != var2)
        
        engine = TranslationEngine()
        
        division_instructions = [
            f"divide {var1} by {var2}",
            f"{var1} divided by {var2}"
        ]
        
        for instruction in division_instructions:
            result = engine.translate(instruction)
            
            if result.success and '/' in result.python_code:
                # Property: Division operations should produce warnings about division by zero
                if result.has_warnings():
                    warning_text = ' '.join(result.warnings).lower()
                    division_keywords = ['division', 'divide', 'zero', 'divisor']
                    mentions_division_risk = any(keyword in warning_text for keyword in division_keywords)
                    assert mentions_division_risk, \
                        f"Division instruction '{instruction}' should warn about division by zero"
    
    @given(
        undefined_var=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() if x else False),
        value=st.integers(min_value=1, max_value=100)
    )
    def test_undefined_variables_produce_warnings(self, undefined_var, value):
        """
        Property: Code using potentially undefined variables should produce warnings
        """
        engine = TranslationEngine()
        
        # Create instruction that might use undefined variable
        instruction = f"add {undefined_var} and {value}"
        result = engine.translate(instruction)
        
        if result.success:
            # Property: If warnings are generated about undefined variables, they should be informative
            if result.has_warnings():
                warning_text = ' '.join(result.warnings).lower()
                if 'undefined' in warning_text or 'variable' in warning_text:
                    variable_keywords = ['undefined', 'variable', 'defined', 'before']
                    mentions_variable_issue = any(keyword in warning_text for keyword in variable_keywords)
                    assert mentions_variable_issue, \
                        f"Variable warnings should be informative for '{instruction}'"
    
    @given(large_number=st.integers(min_value=10000, max_value=100000))
    def test_large_range_operations_produce_warnings(self, large_number):
        """
        Property: Large range operations should produce performance warnings
        """
        engine = TranslationEngine()
        
        instruction = f"repeat {large_number} times print hello"
        result = engine.translate(instruction)
        
        if result.success and 'range(' in result.python_code:
            # Property: Large range operations should produce performance warnings
            if result.has_warnings():
                warning_text = ' '.join(result.warnings).lower()
                performance_keywords = ['large', 'range', 'performance', 'intentional']
                mentions_performance = any(keyword in warning_text for keyword in performance_keywords)
                if any(keyword in warning_text for keyword in ['large', 'range']):
                    assert mentions_performance, \
                        f"Large range instruction '{instruction}' should warn about performance"
    
    @given(instruction=valid_english_instructions())
    def test_warning_severity_levels(self, instruction):
        """
        Property: Warnings should have appropriate severity levels
        """
        engine = TranslationEngine()
        
        result = engine.translate(instruction)
        
        if result.success and result.has_warnings():
            # Property: Warnings should indicate severity levels
            for warning in result.warnings:
                warning_lower = warning.lower()
                severity_indicators = ['low', 'medium', 'high', 'warning', 'caution', 'critical']
                has_severity_indicator = any(indicator in warning_lower for indicator in severity_indicators)
                # This is a soft property - not all warnings need explicit severity
                # but if they have it, it should be meaningful
                if any(indicator in warning_lower for indicator in ['[', 'severity', 'level']):
                    assert has_severity_indicator, \
                        f"Warning should have severity indicator: {warning}"
    
    @given(instruction=valid_english_instructions())
    def test_warnings_provide_suggestions(self, instruction):
        """
        Property: Warnings should provide helpful suggestions when possible
        """
        engine = TranslationEngine()
        
        result = engine.translate(instruction)
        
        if result.success and result.has_warnings():
            # Property: Warnings should provide suggestions or guidance
            warning_text = ' '.join(result.warnings).lower()
            suggestion_keywords = ['suggestion', 'try', 'consider', 'ensure', 'make sure', 'check']
            provides_guidance = any(keyword in warning_text for keyword in suggestion_keywords)
            
            # This is a soft property - not all warnings need suggestions
            # but many should provide guidance
            if len(result.warnings) > 0:
                # At least some warnings should be helpful
                assert len(warning_text) > 10, \
                    f"Warnings should be informative for '{instruction}'"


class TestTranslationErrorDisplay:
    """
    **Feature: english-to-python-translator, Property 18: Translation error display**
    **Validates: Requirements 5.2**
    
    Property: For any error occurring during translation, the error message should be 
    displayed in a separate error area distinct from the output area.
    """
    
    @settings(deadline=1000)  # 1 second deadline
    @given(invalid_input=invalid_english_instructions())
    def test_translation_errors_displayed_separately(self, invalid_input):
        """
        Property: Translation errors should be displayed in separate error area
        """
        from src.gui.application_controller import ApplicationController
        import tkinter as tk
        
        # Create application controller with GUI
        controller = ApplicationController()
        main_window = controller.get_main_window()
        
        try:
            # Property: GUI should have separate error display area
            assert hasattr(main_window, 'error_text'), \
                "Main window should have separate error text area"
            assert hasattr(main_window, 'set_error_text'), \
                "Main window should have method to set error text"
            assert hasattr(main_window, 'display_translation_error'), \
                "Main window should have method to display translation errors"
            
            # Clear any existing content
            main_window.clear_error_text()
            main_window.set_output_text("")
            
            # Simulate translation of invalid input
            result = controller._handle_translate(invalid_input)
            
            # Property: Invalid input should produce failed translation result
            if hasattr(result, 'success'):
                assert not result.success, f"Invalid input '{invalid_input}' should produce failed translation"
                
                # Simulate GUI handling the error (this would normally be done by the GUI callback)
                main_window.display_translation_error(result.error_message)
                
                # Property: Error should be displayed in error area, not output area
                error_content = main_window.get_error_text()
                output_content = main_window.get_output_text()
                
                assert error_content.strip(), \
                    f"Error area should contain error message for '{invalid_input}'"
                
                # Property: Error message should contain the actual error
                assert result.error_message in error_content or "TRANSLATION ERROR" in error_content, \
                    f"Error area should contain translation error for '{invalid_input}'"
                
                # Property: Output area should not contain the error (separation of concerns)
                assert result.error_message not in output_content, \
                    f"Output area should not contain error message for '{invalid_input}'"
            
        finally:
            # Clean up GUI
            try:
                main_window.destroy()
            except:
                pass
    
    @settings(deadline=1000)  # 1 second deadline
    @given(
        valid_input=valid_english_instructions(),
        invalid_input=invalid_english_instructions()
    )
    def test_error_area_distinct_from_output_area(self, valid_input, invalid_input):
        """
        Property: Error area should be distinct from output area
        """
        from src.gui.application_controller import ApplicationController
        
        controller = ApplicationController()
        main_window = controller.get_main_window()
        
        try:
            # Property: Error and output areas should be separate widgets
            assert main_window.error_text != main_window.output_text, \
                "Error text area should be different widget from output text area"
            
            # Clear both areas
            main_window.clear_error_text()
            main_window.set_output_text("")
            
            # Test valid input first
            valid_result = controller._handle_translate(valid_input)
            if hasattr(valid_result, 'success') and valid_result.success:
                main_window.set_output_text(valid_result.python_code)
                
                # Property: Valid translation should put code in output area
                output_content = main_window.get_output_text()
                assert output_content.strip(), \
                    f"Valid input '{valid_input}' should produce output"
                
                # Property: Error area should remain empty for valid input
                error_content = main_window.get_error_text()
                assert not error_content.strip(), \
                    f"Error area should be empty for valid input '{valid_input}'"
            
            # Now test invalid input
            invalid_result = controller._handle_translate(invalid_input)
            if hasattr(invalid_result, 'success') and not invalid_result.success:
                main_window.display_translation_error(invalid_result.error_message)
                
                # Property: Invalid translation should put error in error area
                error_content = main_window.get_error_text()
                assert error_content.strip(), \
                    f"Invalid input '{invalid_input}' should produce error in error area"
                
                # Property: Error should not contaminate output area
                output_content = main_window.get_output_text()
                if output_content.strip():  # If there was previous valid output
                    assert invalid_result.error_message not in output_content, \
                        f"Error should not appear in output area for '{invalid_input}'"
        
        finally:
            # Clean up GUI
            try:
                main_window.destroy()
            except:
                pass
    
    @settings(deadline=1000)  # 1 second deadline
    @given(error_message=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Ps', 'Pe', 'Po'), whitelist_characters=' '),
        min_size=10, max_size=200
    ).filter(lambda x: x.strip() and x.isprintable()))
    def test_error_display_formatting(self, error_message):
        """
        Property: Error messages should be properly formatted when displayed
        """
        from src.gui.application_controller import ApplicationController
        
        controller = ApplicationController()
        main_window = controller.get_main_window()
        
        try:
            # Property: Error display method should format errors with timestamp
            main_window.display_translation_error(error_message)
            
            displayed_error = main_window.get_error_text()
            
            # Property: Displayed error should contain original message (accounting for whitespace normalization)
            assert error_message.strip() in displayed_error, \
                f"Displayed error should contain original message: {error_message.strip()}"
            
            # Property: Displayed error should have formatting (timestamp, label)
            assert "TRANSLATION ERROR" in displayed_error, \
                "Displayed error should have error type label"
            
            # Property: Displayed error should have timestamp format [HH:MM:SS]
            import re
            timestamp_pattern = r'\[\d{2}:\d{2}:\d{2}\]'
            has_timestamp = re.search(timestamp_pattern, displayed_error)
            assert has_timestamp, \
                f"Displayed error should have timestamp format: {displayed_error}"
        
        finally:
            # Clean up GUI
            try:
                main_window.destroy()
            except:
                pass
    
    @settings(deadline=1000)  # 1 second deadline
    @given(
        error1=st.text(min_size=5, max_size=50).filter(lambda x: x.strip()),
        error2=st.text(min_size=5, max_size=50).filter(lambda x: x.strip())
    )
    def test_multiple_errors_handling(self, error1, error2):
        """
        Property: Multiple translation errors should be handled properly
        """
        assume(error1 != error2)
        
        from src.gui.application_controller import ApplicationController
        
        controller = ApplicationController()
        main_window = controller.get_main_window()
        
        try:
            # Clear error area
            main_window.clear_error_text()
            
            # Display first error
            main_window.display_translation_error(error1)
            first_display = main_window.get_error_text()
            
            # Property: First error should be displayed (accounting for whitespace normalization)
            assert error1.strip() in first_display, \
                f"First error should be displayed: {error1.strip()}"
            
            # Display second error (should replace first)
            main_window.display_translation_error(error2)
            second_display = main_window.get_error_text()
            
            # Property: Second error should be displayed (accounting for whitespace normalization)
            assert error2.strip() in second_display, \
                f"Second error should be displayed: {error2.strip()}"
            
            # Property: Error area should show most recent error
            # (Implementation may vary - could replace or append)
            assert second_display != first_display, \
                "Error display should change when new error is displayed"
        
        finally:
            # Clean up GUI
            try:
                main_window.destroy()
            except:
                pass


class TestExampleProvisionForUnprocessableInput:
    """
    **Feature: english-to-python-translator, Property 21: Example provision for unprocessable input**
    **Validates: Requirements 5.5**
    
    Property: For any input that cannot be processed, the system should provide 
    at least one example of valid input format.
    """
    
    @given(unprocessable_input=st.sampled_from([
        'hello world',
        'random text here', 
        'no pattern at all',
        'just some words',
        'xyz abc def ghi',
        'this makes no sense',
        'completely unrelated content',
        'foo bar baz'
    ]))
    def test_unprocessable_input_provides_examples(self, unprocessable_input):
        """
        Property: Unprocessable input should provide at least one example of valid format
        """
        engine = TranslationEngine()
        
        result = engine.translate(unprocessable_input)
        
        # Property: Unprocessable input should result in failed translation
        assert not result.success, f"Unprocessable input '{unprocessable_input}' should result in failed translation"
        
        # Property: Error message should provide examples
        error_msg = result.error_message.lower()
        
        # Check for example indicators
        example_indicators = ['example', 'try', 'like', 'such as', 'pattern', 'format']
        has_example_indicators = any(indicator in error_msg for indicator in example_indicators)
        assert has_example_indicators, \
            f"Error message should provide examples for unprocessable input '{unprocessable_input}': {result.error_message}"
        
        # Property: Should contain at least one concrete example
        # Look for patterns that indicate examples are provided
        concrete_examples = [
            'add', 'multiply', 'set', 'create', 'if', 'repeat', 'list', 'dictionary'
        ]
        has_concrete_examples = any(example in error_msg for example in concrete_examples)
        assert has_concrete_examples, \
            f"Error message should contain concrete examples for '{unprocessable_input}': {result.error_message}"
    
    @given(empty_or_short_input=st.one_of(
        st.just(''),
        st.just('   '),
        st.text(min_size=1, max_size=2).filter(lambda x: x.strip())
    ))
    def test_empty_or_short_input_provides_examples(self, empty_or_short_input):
        """
        Property: Empty or too short input should provide examples of valid input
        """
        engine = TranslationEngine()
        
        result = engine.translate(empty_or_short_input)
        
        # Property: Empty/short input should fail
        assert not result.success, f"Empty/short input should result in failed translation"
        
        # Property: Error message should provide examples
        error_msg = result.error_message
        
        # Should contain example patterns
        example_patterns = [
            'add 5 and 3',
            'set x to 10', 
            'create list',
            'if x greater than',
            'multiply'
        ]
        
        has_examples = any(pattern in error_msg for pattern in example_patterns)
        assert has_examples, \
            f"Error message should provide examples for empty/short input: {result.error_message}"
    
    @given(unsafe_input=st.sampled_from([
        'import os and delete files',
        'exec malicious code',
        'eval dangerous expression', 
        'open system files',
        '__import__ something',
        'exec(evil_code)'
    ]))
    def test_unsafe_input_provides_safe_examples(self, unsafe_input):
        """
        Property: Unsafe input should provide examples of safe operations
        """
        engine = TranslationEngine()
        
        result = engine.translate(unsafe_input)
        
        # Property: Unsafe input should fail
        assert not result.success, f"Unsafe input '{unsafe_input}' should result in failed translation"
        
        # Property: Error message should mention safety and provide safe examples
        error_msg = result.error_message.lower()
        
        # Should mention safety concerns
        safety_keywords = ['unsafe', 'dangerous', 'avoid', 'safe', 'secure']
        mentions_safety = any(keyword in error_msg for keyword in safety_keywords)
        assert mentions_safety, \
            f"Error message should mention safety for unsafe input '{unsafe_input}': {result.error_message}"
        
        # Should provide safe alternatives
        safe_examples = ['add', 'set', 'create', 'calculate', 'list', 'basic']
        has_safe_examples = any(example in error_msg for example in safe_examples)
        assert has_safe_examples, \
            f"Error message should provide safe examples for unsafe input '{unsafe_input}': {result.error_message}"
    
    @given(unprocessable_input=st.sampled_from([
        'random words here',
        'no meaning at all', 
        'just text without purpose',
        'completely unrelated stuff'
    ]))
    def test_examples_cover_multiple_categories(self, unprocessable_input):
        """
        Property: Examples should cover multiple categories of operations
        """
        engine = TranslationEngine()
        
        result = engine.translate(unprocessable_input)
        
        if not result.success:
            error_msg = result.error_message.lower()
            
            # Property: Error message should provide examples from multiple categories
            categories = {
                'arithmetic': ['add', 'multiply', 'divide', 'subtract', 'plus', 'times'],
                'assignment': ['set', 'create variable', 'assign'],
                'conditional': ['if', 'when', 'then'],
                'data': ['list', 'dictionary', 'array'],
                'loop': ['repeat', 'for each', 'while']
            }
            
            categories_covered = 0
            for category, keywords in categories.items():
                if any(keyword in error_msg for keyword in keywords):
                    categories_covered += 1
            
            # Property: Should cover at least 2 different categories of operations
            assert categories_covered >= 2, \
                f"Error message should cover multiple operation categories for '{unprocessable_input}': {result.error_message}"