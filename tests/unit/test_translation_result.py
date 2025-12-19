"""
Unit tests for TranslationResult and ExecutionResult data models
"""

import pytest
from datetime import datetime
from src.models import TranslationResult, ExecutionResult


class TestExecutionResult:
    """Test cases for ExecutionResult class"""
    
    def test_execution_result_creation(self):
        """Test basic execution result creation"""
        result = ExecutionResult(
            success=True,
            output="Hello World",
            execution_time=0.5
        )
        
        assert result.success is True
        assert result.output == "Hello World"
        assert result.execution_time == 0.5
        assert result.error_message == ""
    
    def test_execution_result_validation(self):
        """Test execution result validation"""
        # Negative execution time should raise error
        with pytest.raises(ValueError, match="Execution time cannot be negative"):
            ExecutionResult(success=True, execution_time=-1.0)
    
    def test_has_output(self):
        """Test output detection"""
        # Result with output
        result_with_output = ExecutionResult(success=True, output="Hello")
        assert result_with_output.has_output()
        
        # Result with stdout
        result_with_stdout = ExecutionResult(success=True, stdout="Hello")
        assert result_with_stdout.has_output()
        
        # Result without output
        result_no_output = ExecutionResult(success=True)
        assert not result_no_output.has_output()
    
    def test_has_error(self):
        """Test error detection"""
        # Failed result
        failed_result = ExecutionResult(success=False)
        assert failed_result.has_error()
        
        # Result with error message
        result_with_error = ExecutionResult(success=True, error_message="Error occurred")
        assert result_with_error.has_error()
        
        # Result with stderr
        result_with_stderr = ExecutionResult(success=True, stderr="Error")
        assert result_with_stderr.has_error()
        
        # Successful result without errors
        success_result = ExecutionResult(success=True, output="OK")
        assert not success_result.has_error()
    
    def test_combined_output(self):
        """Test combined output functionality"""
        result = ExecutionResult(
            success=True,
            output="Main output",
            stdout="Standard output"
        )
        
        combined = result.get_combined_output()
        assert "Main output" in combined
        assert "Standard output" in combined
    
    def test_combined_error(self):
        """Test combined error functionality"""
        result = ExecutionResult(
            success=False,
            error_message="Main error",
            stderr="Standard error"
        )
        
        combined = result.get_combined_error()
        assert "Main error" in combined
        assert "Standard error" in combined
    
    def test_to_dict_conversion(self):
        """Test converting execution result to dictionary"""
        result = ExecutionResult(
            success=True,
            output="Hello",
            execution_time=1.5,
            return_value=42
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["output"] == "Hello"
        assert result_dict["execution_time"] == 1.5
        assert result_dict["return_value"] == 42


class TestTranslationResult:
    """Test cases for TranslationResult class"""
    
    def test_translation_result_creation(self):
        """Test basic translation result creation"""
        result = TranslationResult(
            success=True,
            python_code="print('Hello')",
            original_text="say hello"
        )
        
        assert result.success is True
        assert result.python_code == "print('Hello')"
        assert result.original_text == "say hello"
        assert result.warnings == []
    
    def test_translation_result_validation(self):
        """Test translation result validation"""
        # Negative translation time should raise error
        with pytest.raises(ValueError, match="Translation time cannot be negative"):
            TranslationResult(success=True, translation_time=-1.0)
        
        # Successful translation without code should raise error
        with pytest.raises(ValueError, match="Successful translation must have non-empty Python code"):
            TranslationResult(success=True, python_code="")
    
    def test_add_warning(self):
        """Test adding warnings to translation result"""
        result = TranslationResult(success=True, python_code="x = 1")
        
        result.add_warning("This is a warning")
        result.add_warning("Another warning")
        
        assert len(result.warnings) == 2
        assert "This is a warning" in result.warnings
        assert result.has_warnings()
        
        # Empty warning should not be added
        result.add_warning("")
        result.add_warning("   ")
        assert len(result.warnings) == 2
    
    def test_execution_result_integration(self):
        """Test integration with execution result"""
        exec_result = ExecutionResult(success=True, output="42")
        translation_result = TranslationResult(
            success=True,
            python_code="print(42)",
            execution_result=exec_result
        )
        
        assert translation_result.has_execution_result()
        assert translation_result.execution_result.output == "42"
    
    def test_is_executable(self):
        """Test executable check"""
        # Successful translation with code should be executable
        executable_result = TranslationResult(
            success=True,
            python_code="x = 1 + 2"
        )
        assert executable_result.is_executable()
        
        # Failed translation should not be executable
        failed_result = TranslationResult(success=False)
        assert not failed_result.is_executable()
        
        # Translation with critical errors should not be executable
        error_result = TranslationResult(
            success=True,
            python_code="x = 1",
            error_message="SyntaxError: invalid syntax"
        )
        assert not error_result.is_executable()
    
    def test_has_critical_errors(self):
        """Test critical error detection"""
        # No errors
        clean_result = TranslationResult(success=True, python_code="x = 1")
        assert not clean_result.has_critical_errors()
        
        # Syntax error
        syntax_error_result = TranslationResult(
            success=False,
            error_message="SyntaxError: invalid syntax"
        )
        assert syntax_error_result.has_critical_errors()
        
        # Name error
        name_error_result = TranslationResult(
            success=False,
            error_message="NameError: name 'x' is not defined"
        )
        assert name_error_result.has_critical_errors()
    
    def test_get_formatted_code(self):
        """Test code formatting"""
        result = TranslationResult(
            success=True,
            python_code="  x = 1  \n  \n  y = 2  \n"
        )
        
        formatted = result.get_formatted_code()
        lines = formatted.split('\n')
        
        assert "x = 1" in lines
        assert "y = 2" in lines
        assert "" not in lines  # Empty lines should be removed
    
    def test_get_summary(self):
        """Test summary generation"""
        # Successful translation
        success_result = TranslationResult(success=True, python_code="x = 1")
        summary = success_result.get_summary()
        assert "✓ Translation successful" in summary
        
        # Successful translation with warnings
        warning_result = TranslationResult(success=True, python_code="x = 1")
        warning_result.add_warning("Test warning")
        summary = warning_result.get_summary()
        assert "with 1 warnings" in summary
        
        # Failed translation
        failed_result = TranslationResult(success=False, error_message="Test error")
        summary = failed_result.get_summary()
        assert "✗ Translation failed" in summary
        assert "Test error" in summary
    
    def test_to_dict_conversion(self):
        """Test converting translation result to dictionary"""
        exec_result = ExecutionResult(success=True, output="Hello")
        result = TranslationResult(
            success=True,
            python_code="print('Hello')",
            original_text="say hello",
            execution_result=exec_result
        )
        result.add_warning("Test warning")
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["python_code"] == "print('Hello')"
        assert result_dict["original_text"] == "say hello"
        assert result_dict["warnings"] == ["Test warning"]
        assert "execution_result" in result_dict
        assert "timestamp" in result_dict
    
    def test_from_dict_conversion(self):
        """Test creating translation result from dictionary"""
        data = {
            "success": True,
            "python_code": "print('Hello')",
            "original_text": "say hello",
            "warnings": ["Test warning"],
            "translation_time": 1.5,
            "execution_result": {
                "success": True,
                "output": "Hello",
                "execution_time": 0.1
            },
            "metadata": {"source": "test"}
        }
        
        result = TranslationResult.from_dict(data)
        
        assert result.success is True
        assert result.python_code == "print('Hello')"
        assert result.original_text == "say hello"
        assert result.warnings == ["Test warning"]
        assert result.translation_time == 1.5
        assert result.execution_result is not None
        assert result.execution_result.output == "Hello"
        assert result.metadata == {"source": "test"}
    
    def test_create_success_factory(self):
        """Test success factory method"""
        result = TranslationResult.create_success(
            python_code="x = 1 + 2",
            original_text="add 1 and 2",
            translation_time=0.5
        )
        
        assert result.success is True
        assert result.python_code == "x = 1 + 2"
        assert result.original_text == "add 1 and 2"
        assert result.translation_time == 0.5
        assert result.error_message == ""
    
    def test_create_error_factory(self):
        """Test error factory method"""
        result = TranslationResult.create_error(
            error_message="Could not parse input",
            original_text="invalid input",
            translation_time=0.1
        )
        
        assert result.success is False
        assert result.error_message == "Could not parse input"
        assert result.original_text == "invalid input"
        assert result.translation_time == 0.1
        assert result.python_code == ""
    
    def test_round_trip_conversion(self):
        """Test that to_dict and from_dict are inverse operations"""
        original = TranslationResult(
            success=True,
            python_code="result = x + y",
            original_text="add x and y",
            translation_time=1.0
        )
        original.add_warning("Test warning")
        
        # Convert to dict and back
        data = original.to_dict()
        reconstructed = TranslationResult.from_dict(data)
        
        # Should be equivalent
        assert reconstructed.success == original.success
        assert reconstructed.python_code == original.python_code
        assert reconstructed.original_text == original.original_text
        assert reconstructed.warnings == original.warnings
        assert reconstructed.translation_time == original.translation_time