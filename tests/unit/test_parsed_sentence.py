"""
Unit tests for ParsedSentence data model
"""

import pytest
from src.models import ParsedSentence, Operation, Condition, PatternType


class TestOperation:
    """Test cases for Operation class"""
    
    def test_operation_creation(self):
        """Test basic operation creation"""
        op = Operation(
            operation_type="add",
            operands=["x", "y"],
            result_variable="result"
        )
        
        assert op.operation_type == "add"
        assert op.operands == ["x", "y"]
        assert op.result_variable == "result"
    
    def test_operation_validation(self):
        """Test operation validation"""
        # Empty operation type should raise error
        with pytest.raises(ValueError, match="Operation type cannot be empty"):
            Operation(operation_type="")
        
        # Invalid operation type should raise error
        with pytest.raises(ValueError, match="Invalid operation type"):
            Operation(operation_type="invalid_op")
    
    def test_operation_type_checks(self):
        """Test operation type checking methods"""
        arithmetic_op = Operation(operation_type="add", operands=["1", "2"])
        assert arithmetic_op.is_arithmetic()
        assert not arithmetic_op.is_assignment()
        assert not arithmetic_op.is_data_operation()
        
        assignment_op = Operation(operation_type="assign", operands=["x", "5"])
        assert not assignment_op.is_arithmetic()
        assert assignment_op.is_assignment()
        assert not assignment_op.is_data_operation()
        
        data_op = Operation(operation_type="create", operands=["list"])
        assert not data_op.is_arithmetic()
        assert not data_op.is_assignment()
        assert data_op.is_data_operation()


class TestCondition:
    """Test cases for Condition class"""
    
    def test_condition_creation(self):
        """Test basic condition creation"""
        cond = Condition(
            condition_text="x > 5",
            condition_type="if",
            variables_used=["x"]
        )
        
        assert cond.condition_text == "x > 5"
        assert cond.condition_type == "if"
        assert cond.variables_used == ["x"]
    
    def test_condition_validation(self):
        """Test condition validation"""
        # Empty condition text should raise error
        with pytest.raises(ValueError, match="Condition text cannot be empty"):
            Condition(condition_text="", condition_type="if")


class TestParsedSentence:
    """Test cases for ParsedSentence class"""
    
    def test_parsed_sentence_creation(self):
        """Test basic parsed sentence creation"""
        sentence = ParsedSentence(
            original_text="add x and y",
            pattern_type=PatternType.ARITHMETIC
        )
        
        assert sentence.original_text == "add x and y"
        assert sentence.pattern_type == PatternType.ARITHMETIC
        assert sentence.variables == {}
        assert sentence.operations == []
        assert sentence.conditions == []
    
    def test_parsed_sentence_validation(self):
        """Test parsed sentence validation"""
        # Empty original text should raise error
        with pytest.raises(ValueError, match="Original text cannot be empty"):
            ParsedSentence(original_text="")
    
    def test_add_variable(self):
        """Test adding variables to parsed sentence"""
        sentence = ParsedSentence(original_text="test sentence")
        
        sentence.add_variable("x", 5)
        sentence.add_variable("y", "hello")
        
        assert sentence.variables["x"] == 5
        assert sentence.variables["y"] == "hello"
        assert sentence.get_variable_names() == ["x", "y"]
        
        # Empty variable name should raise error
        with pytest.raises(ValueError, match="Variable name cannot be empty"):
            sentence.add_variable("", 10)
    
    def test_add_operation(self):
        """Test adding operations to parsed sentence"""
        sentence = ParsedSentence(original_text="test sentence")
        operation = Operation(operation_type="add", operands=["x", "y"])
        
        sentence.add_operation(operation)
        
        assert len(sentence.operations) == 1
        assert sentence.operations[0] == operation
        assert sentence.has_arithmetic_operations()
        
        # Invalid operation type should raise error
        with pytest.raises(TypeError, match="Expected Operation instance"):
            sentence.add_operation("not an operation")
    
    def test_add_condition(self):
        """Test adding conditions to parsed sentence"""
        sentence = ParsedSentence(original_text="test sentence")
        condition = Condition(condition_text="x > 5", condition_type="if")
        
        sentence.add_condition(condition)
        
        assert len(sentence.conditions) == 1
        assert sentence.conditions[0] == condition
        assert sentence.has_conditions()
        
        # Invalid condition type should raise error
        with pytest.raises(TypeError, match="Expected Condition instance"):
            sentence.add_condition("not a condition")
    
    def test_validity_check(self):
        """Test parsed sentence validity checking"""
        # Empty sentence should be invalid
        sentence = ParsedSentence(original_text="test")
        assert not sentence.is_valid()
        
        # Sentence with unknown pattern should be invalid
        sentence.pattern_type = PatternType.UNKNOWN
        sentence.add_variable("x", 5)
        assert not sentence.is_valid()
        
        # Sentence with known pattern and content should be valid
        sentence.pattern_type = PatternType.ARITHMETIC
        assert sentence.is_valid()
    
    def test_to_dict_conversion(self):
        """Test converting parsed sentence to dictionary"""
        sentence = ParsedSentence(
            original_text="add x and y",
            pattern_type=PatternType.ARITHMETIC
        )
        sentence.add_variable("x", 5)
        sentence.add_operation(Operation(operation_type="add", operands=["x", "y"]))
        sentence.add_condition(Condition(condition_text="x > 0", condition_type="if"))
        
        result_dict = sentence.to_dict()
        
        assert result_dict["original_text"] == "add x and y"
        assert result_dict["pattern_type"] == "arithmetic"
        assert result_dict["variables"] == {"x": 5}
        assert len(result_dict["operations"]) == 1
        assert len(result_dict["conditions"]) == 1
    
    def test_from_dict_conversion(self):
        """Test creating parsed sentence from dictionary"""
        data = {
            "original_text": "add x and y",
            "pattern_type": "arithmetic",
            "variables": {"x": 5, "y": 3},
            "operations": [
                {
                    "operation_type": "add",
                    "operands": ["x", "y"],
                    "result_variable": "result"
                }
            ],
            "conditions": [
                {
                    "condition_text": "x > 0",
                    "condition_type": "if",
                    "variables_used": ["x"]
                }
            ],
            "metadata": {"source": "test"}
        }
        
        sentence = ParsedSentence.from_dict(data)
        
        assert sentence.original_text == "add x and y"
        assert sentence.pattern_type == PatternType.ARITHMETIC
        assert sentence.variables == {"x": 5, "y": 3}
        assert len(sentence.operations) == 1
        assert len(sentence.conditions) == 1
        assert sentence.metadata == {"source": "test"}
    
    def test_round_trip_conversion(self):
        """Test that to_dict and from_dict are inverse operations"""
        original = ParsedSentence(
            original_text="create list with items",
            pattern_type=PatternType.DATA_OPERATION
        )
        original.add_variable("items", ["a", "b", "c"])
        original.add_operation(Operation(operation_type="create", operands=["list"]))
        
        # Convert to dict and back
        data = original.to_dict()
        reconstructed = ParsedSentence.from_dict(data)
        
        # Should be equivalent
        assert reconstructed.original_text == original.original_text
        assert reconstructed.pattern_type == original.pattern_type
        assert reconstructed.variables == original.variables
        assert len(reconstructed.operations) == len(original.operations)
        assert reconstructed.operations[0].operation_type == original.operations[0].operation_type