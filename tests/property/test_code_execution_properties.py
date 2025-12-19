"""
Property-based tests for Code Execution Service functionality
**Feature: english-to-python-translator, Property 22: Code execution functionality**
**Validates: Requirements 6.1**
"""

import pytest
from hypothesis import given, strategies as st, assume
import ast
import time
from src.services import CodeExecutionService, ExecutionConfig
from src.models.translation_result import ExecutionResult


# Hypothesis strategies for generating test data
@st.composite
def valid_python_code(draw):
    """Generate valid Python code that should be executable"""
    code_type = draw(st.sampled_from(['arithmetic', 'assignment', 'print', 'simple_loop', 'conditional']))
    
    if code_type == 'arithmetic':
        var1 = draw(st.integers(min_value=1, max_value=100))
        var2 = draw(st.integers(min_value=1, max_value=100))
        operation = draw(st.sampled_from(['+', '-', '*']))
        return f"result = {var1} {operation} {var2}\nprint(result)"
    
    elif code_type == 'assignment':
        var_name = draw(st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() and x.isascii() if x else False))
        value = draw(st.integers(min_value=0, max_value=1000))
        return f"{var_name} = {value}\nprint({var_name})"
    
    elif code_type == 'print':
        message = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=1, max_size=20
        ).filter(lambda x: x.strip() and '"' not in x))
        return f'print("{message}")'
    
    elif code_type == 'simple_loop':
        count = draw(st.integers(min_value=1, max_value=5))
        return f"for i in range({count}):\n    print(i)"
    
    else:  # conditional
        condition_value = draw(st.booleans())
        return f"if {condition_value}:\n    print('true')\nelse:\n    print('false')"


@st.composite
def invalid_python_code(draw):
    """Generate invalid Python code that should produce errors"""
    error_type = draw(st.sampled_from(['syntax_error', 'indentation_error', 'name_error', 'runtime_error']))
    
    if error_type == 'syntax_error':
        return draw(st.sampled_from([
            'print("hello"',  # Missing closing parenthesis
            'if True\n    print("test")',  # Missing colon
            'x = 1 +',  # Incomplete expression
            'def func(\n    pass',  # Invalid function definition
        ]))
    
    elif error_type == 'indentation_error':
        return draw(st.sampled_from([
            'if True:\nprint("test")',  # Missing indentation
            'for i in range(3):\n  print(i)\n    print("extra")',  # Inconsistent indentation
        ]))
    
    elif error_type == 'name_error':
        return draw(st.sampled_from([
            'print(undefined_variable)',  # Undefined variable
            'result = x + y',  # Undefined variables
        ]))
    
    else:  # runtime_error
        return draw(st.sampled_from([
            'result = 1 / 0',  # Division by zero
            'x = [1, 2, 3]\nprint(x[10])',  # Index error
        ]))


@st.composite
def interactive_python_code(draw):
    """Generate Python code that requires user input"""
    input_type = draw(st.sampled_from(['simple_input', 'multiple_inputs', 'input_with_prompt']))
    
    if input_type == 'simple_input':
        return 'name = input()\nprint("Hello " + name)'
    
    elif input_type == 'multiple_inputs':
        return 'x = input("Enter first number: ")\ny = input("Enter second number: ")\nprint(int(x) + int(y))'
    
    else:  # input_with_prompt
        prompt = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=1, max_size=20
        ).filter(lambda x: x.strip() and '"' not in x))
        return f'response = input("{prompt}: ")\nprint("You entered:", response)'


class TestCodeExecutionFunctionality:
    """
    **Feature: english-to-python-translator, Property 22: Code execution functionality**
    **Validates: Requirements 6.1**
    
    Property: For any generated Python code, pressing the run button should execute 
    the code and capture its output or errors.
    """
    
    @given(code=valid_python_code())
    def test_valid_code_execution_produces_result(self, code):
        """
        Property: Valid Python code should execute and produce a result
        """
        service = CodeExecutionService()
        
        # Property: Code execution should produce an ExecutionResult
        result = service.execute_code(code)
        
        assert isinstance(result, ExecutionResult), \
            f"Code execution should return ExecutionResult for code: {code}"
        
        # Property: ExecutionResult should have proper structure
        assert isinstance(result.success, bool), "ExecutionResult.success should be boolean"
        assert isinstance(result.output, str), "ExecutionResult.output should be string"
        assert isinstance(result.error_message, str), "ExecutionResult.error_message should be string"
        assert isinstance(result.execution_time, (int, float)), "ExecutionResult.execution_time should be numeric"
        assert result.execution_time >= 0, "Execution time should be non-negative"
    
    @given(code=valid_python_code())
    def test_successful_code_execution_captures_output(self, code):
        """
        Property: Successfully executed code should capture output
        """
        service = CodeExecutionService()
        
        result = service.execute_code(code)
        
        if result.success:
            # Property: Successful execution should have output or no errors
            if 'print(' in code:
                # Code with print statements should produce output
                assert result.output.strip() or result.stdout.strip(), \
                    f"Code with print should produce output: {code}"
            
            # Property: Successful execution should not have error messages
            assert not result.error_message.strip(), \
                f"Successful execution should not have error message: {code}"
    
    @given(code=invalid_python_code())
    def test_invalid_code_execution_produces_error(self, code):
        """
        Property: Invalid Python code should produce error messages
        """
        service = CodeExecutionService()
        
        result = service.execute_code(code)
        
        # Property: Invalid code should result in failed execution
        assert not result.success, f"Invalid code should fail execution: {code}"
        
        # Property: Failed execution should have error message
        assert result.error_message.strip(), \
            f"Failed execution should have error message for code: {code}"
        
        # Property: Error message should be informative
        error_msg = result.error_message.lower()
        error_keywords = ['error', 'exception', 'invalid', 'syntax', 'name', 'indentation']
        has_error_info = any(keyword in error_msg for keyword in error_keywords)
        assert has_error_info, \
            f"Error message should be informative for code: {code}, got: {result.error_message}"
    
    @given(
        var_name=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() and x.isascii() if x else False),
        value=st.integers(min_value=0, max_value=100)
    )
    def test_code_execution_preserves_variable_values(self, var_name, value):
        """
        Property: Code execution should properly handle variable assignments
        """
        service = CodeExecutionService()
        
        code = f"{var_name} = {value}\nprint({var_name})"
        result = service.execute_code(code)
        
        if result.success:
            # Property: Variable assignment and print should produce the value in output
            output = result.get_combined_output().strip()
            assert str(value) in output, \
                f"Variable assignment should produce correct output for {var_name} = {value}"
    
    @given(
        num1=st.integers(min_value=1, max_value=50),
        num2=st.integers(min_value=1, max_value=50),
        operation=st.sampled_from(['+', '-', '*'])
    )
    def test_arithmetic_code_execution_correctness(self, num1, num2, operation):
        """
        Property: Arithmetic operations should produce mathematically correct results
        """
        service = CodeExecutionService()
        
        code = f"result = {num1} {operation} {num2}\nprint(result)"
        result = service.execute_code(code)
        
        if result.success:
            # Calculate expected result
            if operation == '+':
                expected = num1 + num2
            elif operation == '-':
                expected = num1 - num2
            else:  # '*'
                expected = num1 * num2
            
            # Property: Arithmetic execution should produce correct mathematical result
            output = result.get_combined_output().strip()
            assert str(expected) in output, \
                f"Arithmetic {num1} {operation} {num2} should produce {expected}, got output: {output}"
    
    @given(count=st.integers(min_value=1, max_value=5))
    def test_loop_execution_produces_expected_iterations(self, count):
        """
        Property: Loop execution should produce expected number of iterations
        """
        service = CodeExecutionService()
        
        code = f"for i in range({count}):\n    print(i)"
        result = service.execute_code(code)
        
        if result.success:
            # Property: Loop should produce output for each iteration
            output_lines = result.get_combined_output().strip().split('\n')
            output_lines = [line.strip() for line in output_lines if line.strip()]
            
            assert len(output_lines) == count, \
                f"Loop with range({count}) should produce {count} lines of output, got {len(output_lines)}"
            
            # Property: Loop should produce correct sequence
            for i in range(count):
                assert str(i) in output_lines, \
                    f"Loop output should contain {i} for range({count})"
    
    @given(code=valid_python_code())
    def test_execution_timing_recorded(self, code):
        """
        Property: Code execution should record timing information
        """
        service = CodeExecutionService()
        
        result = service.execute_code(code)
        
        # Property: Execution time should be recorded and reasonable
        assert result.execution_time >= 0, "Execution time should be non-negative"
        assert result.execution_time < 10.0, \
            f"Execution time should be reasonable for simple code: {code}, got {result.execution_time}"
    
    @given(code=st.text(min_size=1, max_size=100))
    def test_execution_service_robustness(self, code):
        """
        Property: Execution service should handle any input without crashing
        """
        service = CodeExecutionService()
        
        # Property: Service should not crash on any input
        try:
            result = service.execute_code(code)
            
            # Property: Result should have proper structure regardless of input
            assert isinstance(result, ExecutionResult)
            assert isinstance(result.success, bool)
            assert isinstance(result.output, str)
            assert isinstance(result.error_message, str)
            assert isinstance(result.execution_time, (int, float))
            
        except Exception as e:
            pytest.fail(f"Execution service crashed on input '{code}': {e}")
    
    @given(timeout=st.floats(min_value=0.1, max_value=2.0))
    def test_execution_timeout_configuration(self, timeout):
        """
        Property: Execution service should respect timeout configuration
        """
        config = ExecutionConfig(timeout_seconds=timeout)
        service = CodeExecutionService(config)
        
        # Create code that might take some time
        code = "import time\nfor i in range(100):\n    time.sleep(0.01)\n    print(i)"
        
        start_time = time.time()
        result = service.execute_code(code)
        actual_time = time.time() - start_time
        
        # Property: Execution should not significantly exceed configured timeout
        # Allow some buffer for overhead
        max_allowed_time = timeout + 1.0
        assert actual_time <= max_allowed_time, \
            f"Execution should respect timeout {timeout}s, took {actual_time}s"
    
    @given(code=valid_python_code())
    def test_execution_isolation(self, code):
        """
        Property: Code execution should be isolated between runs
        """
        service = CodeExecutionService()
        
        # Execute the same code twice
        result1 = service.execute_code(code)
        result2 = service.execute_code(code)
        
        # Property: Multiple executions should produce consistent results
        assert result1.success == result2.success, \
            f"Execution consistency failed for code: {code}"
        
        if result1.success and result2.success:
            # Normalize output for comparison
            output1 = result1.get_combined_output().strip()
            output2 = result2.get_combined_output().strip()
            assert output1 == output2, \
                f"Execution should be consistent for code: {code}"


class TestRuntimeErrorHandling:
    """
    **Feature: english-to-python-translator, Property 24: Runtime error handling**
    **Validates: Requirements 6.3**
    
    Property: For any code execution that raises a runtime error, the system 
    should display a clear error message including the error type and description.
    """
    
    @given(error_code=st.sampled_from([
        'result = 1 / 0',  # ZeroDivisionError
        'x = [1, 2, 3]\nprint(x[10])',  # IndexError
        'x = {"a": 1}\nprint(x["b"])',  # KeyError
        'x = "hello"\nprint(x[10])',  # IndexError
    ]))
    def test_runtime_errors_produce_clear_messages(self, error_code):
        """
        Property: Runtime errors should produce clear, informative error messages
        """
        service = CodeExecutionService()
        
        result = service.execute_code(error_code)
        
        # Property: Runtime errors should result in failed execution
        assert not result.success, f"Runtime error code should fail: {error_code}"
        
        # Property: Error message should be clear and informative
        error_msg = result.error_message
        assert error_msg.strip(), f"Runtime error should have error message for: {error_code}"
        
        # Property: Error message should include error type
        error_types = ['ZeroDivisionError', 'IndexError', 'KeyError', 'TypeError', 'ValueError', 'NameError']
        has_error_type = any(error_type in error_msg for error_type in error_types)
        assert has_error_type, \
            f"Error message should include error type for: {error_code}, got: {error_msg}"
    
    @given(undefined_var=st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
        min_size=1, max_size=8
    ).filter(lambda x: (
        x.isidentifier() and 
        x.isascii() and 
        x not in {
            # Safe builtins from CodeExecutionService
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
            'getattr', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min',
            'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
            'str', 'sum', 'tuple', 'type', 'zip',
            # Python keywords and constants
            'True', 'False', 'None'
        } and
        not __import__('keyword').iskeyword(x)
    ) if x else False))
    def test_name_errors_include_variable_name(self, undefined_var):
        """
        Property: NameError should include the undefined variable name in error message
        """
        service = CodeExecutionService()
        
        code = f"print({undefined_var})"
        result = service.execute_code(code)
        
        # Property: NameError should result in failed execution
        assert not result.success, f"Undefined variable should cause NameError: {code}"
        
        # Property: Error message should mention NameError and the variable name
        error_msg = result.error_message
        assert 'NameError' in error_msg, f"Should be NameError for undefined variable: {error_msg}"
        assert undefined_var in error_msg, \
            f"Error message should mention variable '{undefined_var}': {error_msg}"
    
    @given(
        numerator=st.integers(min_value=1, max_value=100),
        denominator=st.just(0)
    )
    def test_division_by_zero_error_handling(self, numerator, denominator):
        """
        Property: Division by zero should produce ZeroDivisionError with clear message
        """
        service = CodeExecutionService()
        
        code = f"result = {numerator} / {denominator}\nprint(result)"
        result = service.execute_code(code)
        
        # Property: Division by zero should fail
        assert not result.success, f"Division by zero should fail: {code}"
        
        # Property: Should produce ZeroDivisionError
        error_msg = result.error_message
        assert 'ZeroDivisionError' in error_msg, \
            f"Division by zero should produce ZeroDivisionError: {error_msg}"
        
        # Property: Error message should be descriptive
        descriptive_keywords = ['division', 'zero', 'divide']
        has_description = any(keyword in error_msg.lower() for keyword in descriptive_keywords)
        assert has_description, \
            f"ZeroDivisionError should be descriptive: {error_msg}"
    
    @given(
        list_size=st.integers(min_value=1, max_value=5),
        invalid_index=st.integers(min_value=10, max_value=20)
    )
    def test_index_error_handling(self, list_size, invalid_index):
        """
        Property: Index errors should produce clear messages about invalid indices
        """
        service = CodeExecutionService()
        
        # Create list and try to access invalid index
        list_items = ', '.join(str(i) for i in range(list_size))
        code = f"x = [{list_items}]\nprint(x[{invalid_index}])"
        result = service.execute_code(code)
        
        # Property: Invalid index should cause IndexError
        assert not result.success, f"Invalid index should cause error: {code}"
        
        # Property: Should produce IndexError
        error_msg = result.error_message
        assert 'IndexError' in error_msg, f"Invalid index should produce IndexError: {error_msg}"
        
        # Property: Error message should mention index or range
        index_keywords = ['index', 'range', 'out of']
        mentions_index = any(keyword in error_msg.lower() for keyword in index_keywords)
        assert mentions_index, f"IndexError should mention index issue: {error_msg}"
    
    @given(syntax_error_code=st.sampled_from([
        'print("hello"',  # Missing closing parenthesis
        'if True\n    print("test")',  # Missing colon
        'x = 1 +',  # Incomplete expression
    ]))
    def test_syntax_error_handling(self, syntax_error_code):
        """
        Property: Syntax errors should be caught and reported clearly
        """
        service = CodeExecutionService()
        
        result = service.execute_code(syntax_error_code)
        
        # Property: Syntax errors should result in failed execution
        assert not result.success, f"Syntax error should fail: {syntax_error_code}"
        
        # Property: Error message should mention syntax error
        error_msg = result.error_message.lower()
        syntax_keywords = ['syntax', 'error', 'invalid', 'unexpected']
        mentions_syntax = any(keyword in error_msg for keyword in syntax_keywords)
        assert mentions_syntax, \
            f"Syntax error should be clearly identified: {result.error_message}"
    
    @given(error_code=invalid_python_code())
    def test_error_messages_preserve_context(self, error_code):
        """
        Property: Error messages should preserve context about what went wrong
        """
        service = CodeExecutionService()
        
        result = service.execute_code(error_code)
        
        if not result.success:
            # Property: Error messages should be non-empty and informative
            error_msg = result.error_message
            assert error_msg.strip(), f"Error message should not be empty for: {error_code}"
            
            # Property: Error message should be reasonably detailed
            assert len(error_msg.strip()) > 5, \
                f"Error message should be detailed for: {error_code}, got: {error_msg}"
    
    @given(error_code=invalid_python_code())
    def test_error_handling_timing(self, error_code):
        """
        Property: Error handling should not significantly impact execution timing
        """
        service = CodeExecutionService()
        
        start_time = time.time()
        result = service.execute_code(error_code)
        execution_time = time.time() - start_time
        
        # Property: Error handling should be fast
        assert execution_time < 5.0, \
            f"Error handling should be fast for: {error_code}, took {execution_time}s"
        
        # Property: Recorded execution time should be reasonable
        assert result.execution_time >= 0, "Execution time should be non-negative"
        assert result.execution_time < 5.0, \
            f"Recorded execution time should be reasonable: {result.execution_time}s"


class TestUserInputHandlingDuringExecution:
    """
    **Feature: english-to-python-translator, Property 25: User input handling during execution**
    **Validates: Requirements 6.5**
    
    Property: For any generated code that requires user input (input() function), 
    the system should provide an input mechanism and pass the user's input to the executing code.
    """
    
    def mock_input_handler(self, prompt: str) -> str:
        """Mock input handler that returns predictable responses"""
        if 'name' in prompt.lower():
            return 'TestUser'
        elif 'number' in prompt.lower():
            return '42'
        elif 'age' in prompt.lower():
            return '25'
        else:
            return 'DefaultResponse'
    
    @given(input_code=interactive_python_code())
    def test_interactive_code_with_input_handler(self, input_code):
        """
        Property: Interactive code should work with input handler
        """
        service = CodeExecutionService()
        
        # Property: Code requiring input should work with input handler
        result = service.execute_code(input_code, user_input_handler=self.mock_input_handler)
        
        if 'input(' in input_code:
            if result.success:
                # Property: Interactive code should produce output
                output = result.get_combined_output()
                assert output.strip(), \
                    f"Interactive code should produce output: {input_code}"
                
                # Property: Output should reflect the mock input values
                # For arithmetic operations, check if the result makes sense
                if 'int(x) + int(y)' in input_code:
                    # Should produce 42 + 42 = 84
                    assert '84' in output, \
                        f"Arithmetic with mock inputs should produce 84 for: {input_code}, got: {output}"
                else:
                    # For other operations, check if mock values appear
                    mock_values = ['TestUser', '42', '25', 'DefaultResponse']
                    contains_mock_value = any(value in output for value in mock_values)
                    assert contains_mock_value, \
                        f"Output should contain mock input values for: {input_code}, got: {output}"
    
    @given(
        var_name=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
            min_size=1, max_size=8
        ).filter(lambda x: x.isidentifier() and x.isascii() if x else False)
    )
    def test_simple_input_handling(self, var_name):
        """
        Property: Simple input() calls should work with input handler
        """
        service = CodeExecutionService()
        
        code = f'{var_name} = input("Enter value: ")\nprint("You entered:", {var_name})'
        
        def simple_input_handler(prompt: str) -> str:
            return 'test_value'
        
        result = service.execute_code(code, user_input_handler=simple_input_handler)
        
        if result.success:
            # Property: Input should be captured and used in output
            output = result.get_combined_output()
            assert 'test_value' in output, \
                f"Output should contain input value for: {code}, got: {output}"
    
    @given(
        prompt_text=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=1, max_size=15
        ).filter(lambda x: x.strip() and '"' not in x)
    )
    def test_input_prompt_preservation(self, prompt_text):
        """
        Property: Input prompts should be passed to the input handler
        """
        service = CodeExecutionService()
        
        received_prompts = []
        
        def prompt_capturing_handler(prompt: str) -> str:
            received_prompts.append(prompt)
            return 'response'
        
        code = f'response = input("{prompt_text}")\nprint(response)'
        result = service.execute_code(code, user_input_handler=prompt_capturing_handler)
        
        if result.success:
            # Property: Input handler should receive the prompt
            assert len(received_prompts) > 0, \
                f"Input handler should receive prompts for: {code}"
            
            # Property: Received prompt should contain the original prompt text
            received_prompt = received_prompts[0]
            assert prompt_text in received_prompt, \
                f"Handler should receive original prompt '{prompt_text}', got: {received_prompt}"
    
    def test_multiple_input_calls_handling(self):
        """
        Property: Code with multiple input() calls should handle all inputs
        """
        service = CodeExecutionService()
        
        input_responses = ['first', 'second', 'third']
        response_index = 0
        
        def multi_input_handler(prompt: str) -> str:
            nonlocal response_index
            if response_index < len(input_responses):
                response = input_responses[response_index]
                response_index += 1
                return response
            return 'default'
        
        code = '''
first = input("First: ")
second = input("Second: ")
third = input("Third: ")
print(f"Got: {first}, {second}, {third}")
'''
        
        result = service.execute_code(code, user_input_handler=multi_input_handler)
        
        if result.success:
            # Property: All input values should appear in output
            output = result.get_combined_output()
            for response in input_responses:
                assert response in output, \
                    f"Output should contain all input responses, missing '{response}' in: {output}"
    
    def test_input_without_handler_produces_error(self):
        """
        Property: Code requiring input without handler should produce security error
        """
        service = CodeExecutionService()
        
        code = 'name = input("Enter name: ")\nprint(name)'
        result = service.execute_code(code)  # No input handler provided
        
        # Property: Input without handler should fail
        assert not result.success, "Code requiring input without handler should fail"
        
        # Property: Error should mention input or security
        error_msg = result.error_message.lower()
        input_keywords = ['input', 'security', 'interactive', 'handler']
        mentions_input_issue = any(keyword in error_msg for keyword in input_keywords)
        assert mentions_input_issue, \
            f"Error should mention input issue: {result.error_message}"
    
    @given(
        input_value=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=1, max_size=20
        ).filter(lambda x: x.strip())
    )
    def test_input_value_types_preserved(self, input_value):
        """
        Property: Input values should be preserved as strings
        """
        service = CodeExecutionService()
        
        def value_handler(prompt: str) -> str:
            return input_value
        
        code = 'value = input("Enter: ")\nprint(f"Type: {type(value).__name__}, Value: {value}")'
        result = service.execute_code(code, user_input_handler=value_handler)
        
        if result.success:
            # Property: Input values should be strings
            output = result.get_combined_output()
            assert 'Type: str' in output, \
                f"Input values should be strings, got output: {output}"
            
            # Property: Input value should be preserved
            assert input_value in output, \
                f"Input value should be preserved in output: {output}"
    
    def test_input_handler_exception_handling(self):
        """
        Property: Input handler exceptions should be handled gracefully
        """
        service = CodeExecutionService()
        
        def failing_handler(prompt: str) -> str:
            raise ValueError("Handler failed")
        
        code = 'name = input("Enter name: ")\nprint(name)'
        result = service.execute_code(code, user_input_handler=failing_handler)
        
        # Property: Handler exceptions should result in execution failure
        assert not result.success, "Input handler exceptions should cause execution failure"
        
        # Property: Error message should be informative
        error_msg = result.error_message
        assert error_msg.strip(), "Should have error message for handler exception"
        
        # Property: Error should mention input or handler issue
        error_keywords = ['input', 'handler', 'error', 'exception']
        mentions_handler_issue = any(keyword in error_msg.lower() for keyword in error_keywords)
        assert mentions_handler_issue, \
            f"Error should mention handler issue: {error_msg}"