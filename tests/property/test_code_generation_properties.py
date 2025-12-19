"""
Property-based tests for Code Generator component
Tests correctness properties for code generation functionality
"""

import ast
import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import List, Dict, Any

from src.core.code_generator import CodeGenerator
from src.models.parsed_sentence import ParsedSentence, Operation, Condition, PatternType
from src.models.translation_result import TranslationResult


# Helper strategies for generating test data
@st.composite
def valid_variable_names(draw):
    """Generate valid Python variable names"""
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyz_'))
    rest_chars = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_',
        min_size=0,
        max_size=10
    ))
    return first_char + rest_chars

@st.composite
def arithmetic_operations(draw):
    """Generate arithmetic operations"""
    operation_type = draw(st.sampled_from(['add', 'subtract', 'multiply', 'divide']))
    operand1 = draw(st.one_of(
        st.integers(min_value=-1000, max_value=1000).map(str),
        valid_variable_names()
    ))
    operand2 = draw(st.one_of(
        st.integers(min_value=-1000, max_value=1000).map(str),
        valid_variable_names()
    ))
    result_var = draw(st.one_of(st.none(), valid_variable_names()))
    
    return Operation(
        operation_type=operation_type,
        operands=[operand1, operand2],
        result_variable=result_var
    )

@st.composite
def arithmetic_parsed_sentences(draw):
    """Generate ParsedSentence objects with arithmetic operations"""
    original_text = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    operations = draw(st.lists(arithmetic_operations(), min_size=1, max_size=3))
    variables = draw(st.dictionaries(
        valid_variable_names(),
        st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.text()),
        min_size=0,
        max_size=5
    ))
    
    return ParsedSentence(
        original_text=original_text,
        pattern_type=PatternType.ARITHMETIC,
        operations=operations,
        variables=variables
    )

@st.composite
def conditional_parsed_sentences(draw):
    """Generate ParsedSentence objects with conditional logic"""
    original_text = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    condition_text = draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
    condition = Condition(
        condition_text=condition_text,
        condition_type='if'
    )
    
    then_block = draw(st.sampled_from(['pass', 'print("then")', 'x = 1']))
    else_block = draw(st.one_of(
        st.none(),
        st.sampled_from(['pass', 'print("else")', 'x = 2'])
    ))
    
    metadata = {'then_block': then_block}
    if else_block:
        metadata['else_block'] = else_block
    
    return ParsedSentence(
        original_text=original_text,
        pattern_type=PatternType.CONDITIONAL,
        conditions=[condition],
        metadata=metadata
    )

@st.composite
def loop_parsed_sentences(draw):
    """Generate ParsedSentence objects with loop logic"""
    original_text = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    loop_type = draw(st.sampled_from(['repeat', 'for_each', 'while']))
    body = draw(st.sampled_from(['pass', 'print("loop")', 'x += 1']))
    
    metadata = {'loop_type': loop_type, 'body': body}
    
    if loop_type == 'repeat':
        count = draw(st.integers(min_value=1, max_value=100))
        metadata['count'] = str(count)
    elif loop_type == 'for_each':
        item = draw(valid_variable_names())
        collection = draw(st.sampled_from(['[1, 2, 3]', 'range(5)', 'my_list']))
        metadata['item'] = item
        metadata['collection'] = collection
    elif loop_type == 'while':
        condition = Condition(
            condition_text=draw(st.text(min_size=1, max_size=30).filter(lambda x: x.strip())),
            condition_type='while'
        )
        return ParsedSentence(
            original_text=original_text,
            pattern_type=PatternType.LOOP,
            conditions=[condition],
            metadata=metadata
        )
    
    return ParsedSentence(
        original_text=original_text,
        pattern_type=PatternType.LOOP,
        metadata=metadata
    )

@st.composite
def control_structure_parsed_sentences(draw):
    """Generate ParsedSentence objects with control structures (conditional or loop)"""
    return draw(st.one_of(conditional_parsed_sentences(), loop_parsed_sentences()))

@st.composite
def data_operation_parsed_sentences(draw):
    """Generate ParsedSentence objects with data operations"""
    original_text = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    operation_type = draw(st.sampled_from(['create', 'append']))
    data_type = draw(st.sampled_from(['list', 'dict', 'string']))
    
    if operation_type == 'create':
        if data_type == 'list':
            items = draw(st.lists(st.integers().map(str), min_size=0, max_size=5))
            result_var = draw(valid_variable_names())
            operation = Operation(
                operation_type=operation_type,
                operands=items,
                result_variable=result_var
            )
        elif data_type == 'string':
            value = draw(st.text(max_size=20))
            result_var = draw(valid_variable_names())
            operation = Operation(
                operation_type=operation_type,
                operands=[value],
                result_variable=result_var
            )
        else:  # dict
            items = draw(st.lists(st.text(max_size=10), min_size=0, max_size=3))
            result_var = draw(valid_variable_names())
            operation = Operation(
                operation_type=operation_type,
                operands=items,
                result_variable=result_var
            )
    else:  # append
        list_var = draw(valid_variable_names())
        item = draw(st.one_of(st.integers().map(str), st.text(max_size=10)))
        operation = Operation(
            operation_type=operation_type,
            operands=[list_var, item]
        )
    
    return ParsedSentence(
        original_text=original_text,
        pattern_type=PatternType.DATA_OPERATION,
        operations=[operation],
        metadata={'data_type': data_type}
    )


class TestCodeGenerationProperties:
    """Property-based tests for code generation correctness"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.generator = CodeGenerator()

    @given(arithmetic_parsed_sentences())
    @settings(max_examples=100)
    def test_property_5_generated_code_is_syntactically_valid_arithmetic(self, parsed_sentence):
        """
        **Feature: english-to-python-translator, Property 5: Generated code is syntactically valid**
        **Validates: Requirements 2.1, 2.2**
        
        For any generated Python code, parsing it with Python's AST parser should succeed without syntax errors.
        """
        # Generate code from parsed sentence
        result = self.generator.generate(parsed_sentence)
        
        # If generation was successful, the code should be syntactically valid
        if result.success:
            assert result.python_code.strip(), "Successful generation should produce non-empty code"
            
            # Test that AST can parse the generated code
            try:
                ast.parse(result.python_code)
            except SyntaxError as e:
                pytest.fail(f"Generated code has syntax error: {e}\nCode:\n{result.python_code}")

    @given(arithmetic_parsed_sentences())
    @settings(max_examples=100)
    def test_property_6_arithmetic_operation_translation(self, parsed_sentence):
        """
        **Feature: english-to-python-translator, Property 6: Arithmetic operation translation**
        **Validates: Requirements 2.3**
        
        For any English instruction containing arithmetic operations (add, subtract, multiply, divide), 
        the generated Python code should contain the corresponding Python arithmetic operators (+, -, *, /).
        """
        # Generate code from parsed sentence
        result = self.generator.generate(parsed_sentence)
        
        # If generation was successful, check for correct operators
        if result.success and result.python_code.strip():
            code = result.python_code
            
            # Check that each arithmetic operation in the parsed sentence 
            # has corresponding Python operators in the generated code
            for operation in parsed_sentence.operations:
                if operation.is_arithmetic():
                    if operation.operation_type == 'add':
                        assert '+' in code, f"Addition operation should generate '+' operator. Code: {code}"
                    elif operation.operation_type == 'subtract':
                        assert '-' in code, f"Subtraction operation should generate '-' operator. Code: {code}"
                    elif operation.operation_type == 'multiply':
                        assert '*' in code, f"Multiplication operation should generate '*' operator. Code: {code}"
                    elif operation.operation_type == 'divide':
                        assert '/' in code, f"Division operation should generate '/' operator. Code: {code}"

    @given(control_structure_parsed_sentences())
    @settings(max_examples=100)
    def test_property_7_control_structure_translation(self, parsed_sentence):
        """
        **Feature: english-to-python-translator, Property 7: Control structure translation**
        **Validates: Requirements 2.4**
        
        For any English instruction containing conditional or loop patterns, 
        the generated Python code should contain valid if/else or for/while statements.
        """
        # Generate code from parsed sentence
        result = self.generator.generate(parsed_sentence)
        
        # If generation was successful, check for correct control structures
        if result.success and result.python_code.strip():
            code = result.python_code
            
            if parsed_sentence.pattern_type == PatternType.CONDITIONAL:
                # Should contain if statement
                assert 'if ' in code, f"Conditional pattern should generate 'if' statement. Code: {code}"
                
                # If there's an else block in metadata, should contain else
                if parsed_sentence.metadata.get('else_block'):
                    assert 'else:' in code, f"Conditional with else block should generate 'else:' statement. Code: {code}"
            
            elif parsed_sentence.pattern_type == PatternType.LOOP:
                loop_type = parsed_sentence.metadata.get('loop_type', 'repeat')
                
                if loop_type == 'repeat':
                    assert 'for _ in range(' in code, f"Repeat loop should generate 'for _ in range(' statement. Code: {code}"
                elif loop_type == 'for_each':
                    assert 'for ' in code and ' in ' in code, f"For-each loop should generate 'for ... in ...' statement. Code: {code}"
                elif loop_type == 'while':
                    assert 'while ' in code, f"While loop should generate 'while' statement. Code: {code}"

    @given(data_operation_parsed_sentences())
    @settings(max_examples=100)
    def test_property_8_data_operation_translation(self, parsed_sentence):
        """
        **Feature: english-to-python-translator, Property 8: Data operation translation**
        **Validates: Requirements 2.5**
        
        For any English instruction containing data manipulation patterns, 
        the generated Python code should contain valid list, dictionary, or string operations.
        """
        # Generate code from parsed sentence
        result = self.generator.generate(parsed_sentence)
        
        # If generation was successful, check for correct data operations
        if result.success and result.python_code.strip():
            code = result.python_code
            data_type = parsed_sentence.metadata.get('data_type', 'list')
            
            for operation in parsed_sentence.operations:
                if operation.operation_type == 'create':
                    if data_type == 'list':
                        assert '[' in code and ']' in code, f"List creation should generate '[...]' syntax. Code: {code}"
                    elif data_type == 'dict':
                        assert '{' in code and '}' in code, f"Dict creation should generate '{{...}}' syntax. Code: {code}"
                    elif data_type == 'string':
                        assert '"' in code or "'" in code, f"String creation should generate string literal. Code: {code}"
                
                elif operation.operation_type == 'append':
                    assert '.append(' in code, f"Append operation should generate '.append()' method call. Code: {code}"
