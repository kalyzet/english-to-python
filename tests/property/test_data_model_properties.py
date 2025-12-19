"""
Property-based tests for data model validation
**Feature: english-to-python-translator, Property 13: Variable extraction**
**Validates: Requirements 3.5**
"""

import pytest
from hypothesis import given, strategies as st, assume
from src.models import ParsedSentence, Operation, Condition, PatternType, TranslationResult, ExecutionResult


# Hypothesis strategies for generating test data
@st.composite
def valid_variable_names(draw):
    """Generate valid Python variable names"""
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'))
    rest_chars = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_',
        min_size=0,
        max_size=20
    ))
    return first_char + rest_chars


@st.composite
def valid_operation_types(draw):
    """Generate valid operation types"""
    return draw(st.sampled_from([
        'add', 'subtract', 'multiply', 'divide', 'assign',
        'create', 'append', 'remove', 'update', 'get'
    ]))


@st.composite
def valid_pattern_types(draw):
    """Generate valid pattern types"""
    return draw(st.sampled_from(list(PatternType)))


@st.composite
def variable_values(draw):
    """Generate various types of variable values"""
    return draw(st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(min_size=0, max_size=100),
        st.booleans(),
        st.lists(st.integers(), min_size=0, max_size=10),
        st.dictionaries(st.text(min_size=1, max_size=10), st.integers(), min_size=0, max_size=5)
    ))


class TestVariableExtractionProperty:
    """
    **Feature: english-to-python-translator, Property 13: Variable extraction**
    **Validates: Requirements 3.5**
    
    Property: For any English sentence containing variable names and values, 
    the parser should extract all variable names and their associated values correctly.
    """
    
    @given(
        original_text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        pattern_type=valid_pattern_types(),
        variables=st.dictionaries(
            valid_variable_names(),
            variable_values(),
            min_size=1,
            max_size=10
        )
    )
    def test_variable_extraction_preservation(self, original_text, pattern_type, variables):
        """
        Property: When variables are added to a ParsedSentence, 
        they should be extractable with correct names and values
        """
        # Create parsed sentence
        sentence = ParsedSentence(
            original_text=original_text,
            pattern_type=pattern_type
        )
        
        # Add all variables
        for name, value in variables.items():
            sentence.add_variable(name, value)
        
        # Property: All added variables should be extractable
        extracted_names = sentence.get_variable_names()
        
        # All variable names should be present
        assert set(extracted_names) == set(variables.keys())
        
        # All variable values should be preserved
        for name, expected_value in variables.items():
            assert sentence.variables[name] == expected_value
    
    @given(
        original_text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        variables=st.dictionaries(
            valid_variable_names(),
            variable_values(),
            min_size=0,
            max_size=10
        )
    )
    def test_variable_extraction_round_trip(self, original_text, variables):
        """
        Property: Variables should survive round-trip conversion (to_dict -> from_dict)
        """
        # Create parsed sentence with variables
        sentence = ParsedSentence(
            original_text=original_text,
            pattern_type=PatternType.ARITHMETIC
        )
        
        for name, value in variables.items():
            sentence.add_variable(name, value)
        
        # Convert to dict and back
        sentence_dict = sentence.to_dict()
        reconstructed = ParsedSentence.from_dict(sentence_dict)
        
        # Property: Variables should be preserved exactly
        assert reconstructed.variables == sentence.variables
        assert set(reconstructed.get_variable_names()) == set(sentence.get_variable_names())
    
    @given(
        original_text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        variable_name=valid_variable_names(),
        variable_value=variable_values()
    )
    def test_single_variable_extraction(self, original_text, variable_name, variable_value):
        """
        Property: Adding a single variable should make it extractable
        """
        sentence = ParsedSentence(original_text=original_text)
        
        # Add single variable
        sentence.add_variable(variable_name, variable_value)
        
        # Property: Variable should be extractable
        assert variable_name in sentence.get_variable_names()
        assert sentence.variables[variable_name] == variable_value
        assert len(sentence.get_variable_names()) == 1
    
    @given(
        original_text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        variables=st.dictionaries(
            valid_variable_names(),
            variable_values(),
            min_size=1,
            max_size=5
        )
    )
    def test_variable_overwrite_behavior(self, original_text, variables):
        """
        Property: Overwriting a variable should update its value correctly
        """
        sentence = ParsedSentence(original_text=original_text)
        
        # Add variables
        for name, value in variables.items():
            sentence.add_variable(name, value)
        
        # Pick first variable to overwrite
        first_var_name = list(variables.keys())[0]
        new_value = "overwritten_value"
        
        # Overwrite the variable
        sentence.add_variable(first_var_name, new_value)
        
        # Property: Variable should have new value
        assert sentence.variables[first_var_name] == new_value
        # Property: Number of variables should remain the same
        assert len(sentence.get_variable_names()) == len(variables)


class TestOperationValidationProperty:
    """Property tests for Operation validation"""
    
    @given(
        operation_type=valid_operation_types(),
        operands=st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5),
        result_variable=st.one_of(st.none(), valid_variable_names())
    )
    def test_valid_operation_creation(self, operation_type, operands, result_variable):
        """
        Property: Valid operation parameters should always create a valid Operation
        """
        operation = Operation(
            operation_type=operation_type,
            operands=operands,
            result_variable=result_variable
        )
        
        # Property: Operation should be created successfully
        assert operation.operation_type == operation_type
        assert operation.operands == operands
        assert operation.result_variable == result_variable
        
        # Property: Type checking methods should work correctly
        if operation_type in {'add', 'subtract', 'multiply', 'divide'}:
            assert operation.is_arithmetic()
        elif operation_type == 'assign':
            assert operation.is_assignment()
        elif operation_type in {'create', 'append', 'remove', 'update', 'get'}:
            assert operation.is_data_operation()


class TestTranslationResultProperty:
    """Property tests for TranslationResult validation"""
    
    @given(
        python_code=st.text(min_size=1, max_size=500).filter(lambda x: x.strip()),
        original_text=st.text(min_size=0, max_size=200),
        translation_time=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_successful_translation_result_creation(self, python_code, original_text, translation_time):
        """
        Property: Creating successful translation results should preserve all data
        """
        result = TranslationResult.create_success(
            python_code=python_code,
            original_text=original_text,
            translation_time=translation_time
        )
        
        # Property: All data should be preserved
        assert result.success is True
        assert result.python_code == python_code
        assert result.original_text == original_text
        assert result.translation_time == translation_time
        assert result.error_message == ""
        assert result.is_executable()  # Should be executable if successful
    
    @given(
        error_message=st.text(min_size=1, max_size=200),
        original_text=st.text(min_size=0, max_size=200),
        translation_time=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_error_translation_result_creation(self, error_message, original_text, translation_time):
        """
        Property: Creating error translation results should preserve error information
        """
        result = TranslationResult.create_error(
            error_message=error_message,
            original_text=original_text,
            translation_time=translation_time
        )
        
        # Property: Error information should be preserved
        assert result.success is False
        assert result.error_message == error_message
        assert result.original_text == original_text
        assert result.translation_time == translation_time
        assert result.python_code == ""
        assert not result.is_executable()  # Should not be executable if failed
    
    @given(
        success=st.booleans(),
        python_code=st.text(min_size=0, max_size=500),
        warnings=st.lists(st.text(min_size=1, max_size=100), min_size=0, max_size=5)
    )
    def test_translation_result_round_trip(self, success, python_code, warnings):
        """
        Property: TranslationResult should survive round-trip conversion
        """
        # Skip invalid combinations
        assume(not (success and not python_code.strip()))
        
        result = TranslationResult(
            success=success,
            python_code=python_code
        )
        
        # Add warnings
        for warning in warnings:
            result.add_warning(warning)
        
        # Convert to dict and back
        result_dict = result.to_dict()
        reconstructed = TranslationResult.from_dict(result_dict)
        
        # Property: All important data should be preserved
        assert reconstructed.success == result.success
        assert reconstructed.python_code == result.python_code
        assert reconstructed.warnings == result.warnings


class TestExecutionResultProperty:
    """Property tests for ExecutionResult validation"""
    
    @given(
        success=st.booleans(),
        output=st.text(min_size=0, max_size=1000),
        error_message=st.text(min_size=0, max_size=500),
        execution_time=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        stdout=st.text(min_size=0, max_size=500),
        stderr=st.text(min_size=0, max_size=500)
    )
    def test_execution_result_properties(self, success, output, error_message, execution_time, stdout, stderr):
        """
        Property: ExecutionResult should correctly report its state
        """
        result = ExecutionResult(
            success=success,
            output=output,
            error_message=error_message,
            execution_time=execution_time,
            stdout=stdout,
            stderr=stderr
        )
        
        # Property: Output detection should be correct
        expected_has_output = bool(output.strip() or stdout.strip())
        assert result.has_output() == expected_has_output
        
        # Property: Error detection should be correct
        expected_has_error = not success or bool(error_message.strip() or stderr.strip())
        assert result.has_error() == expected_has_error
        
        # Property: Combined output should include all output sources
        combined_output = result.get_combined_output()
        if output.strip():
            assert output.strip() in combined_output
        if stdout.strip():
            assert stdout.strip() in combined_output
        
        # Property: Combined error should include all error sources
        combined_error = result.get_combined_error()
        if error_message.strip():
            assert error_message.strip() in combined_error
        if stderr.strip():
            assert stderr.strip() in combined_error


class TestDataModelIntegrationProperty:
    """Property tests for data model integration"""
    
    @given(
        original_text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        pattern_type=valid_pattern_types(),
        variables=st.dictionaries(
            valid_variable_names(),
            variable_values(),
            min_size=0,
            max_size=3
        ),
        operations=st.lists(
            st.builds(
                Operation,
                operation_type=valid_operation_types(),
                operands=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=3)
            ),
            min_size=0,
            max_size=3
        )
    )
    def test_parsed_sentence_validity_property(self, original_text, pattern_type, variables, operations):
        """
        Property: ParsedSentence validity should be consistent with its content
        """
        sentence = ParsedSentence(
            original_text=original_text,
            pattern_type=pattern_type
        )
        
        # Add variables and operations
        for name, value in variables.items():
            sentence.add_variable(name, value)
        
        for operation in operations:
            sentence.add_operation(operation)
        
        # Property: Validity should be consistent
        has_content = (
            len(sentence.variables) > 0 or 
            len(sentence.operations) > 0 or 
            len(sentence.conditions) > 0
        )
        has_known_pattern = sentence.pattern_type != PatternType.UNKNOWN
        
        expected_validity = has_content and has_known_pattern
        assert sentence.is_valid() == expected_validity