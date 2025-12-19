"""
Unit tests for Input Parser component
"""

import pytest
from src.core import InputParser, PatternMatcher, Token, TokenType
from src.models import PatternType


class TestPatternMatcher:
    """Test cases for PatternMatcher class"""
    
    def test_arithmetic_patterns(self):
        """Test arithmetic pattern matching"""
        matcher = PatternMatcher()
        
        # Addition patterns
        result = matcher.match_arithmetic("add x and y")
        assert result is not None
        assert result[0] == "add"
        assert "x" in result[1] and "y" in result[1]
        
        result = matcher.match_arithmetic("calculate 5 plus 3")
        assert result is not None
        assert result[0] == "add"
        
        # Multiplication patterns
        result = matcher.match_arithmetic("multiply a by b")
        assert result is not None
        assert result[0] == "multiply"
        
        # No match
        result = matcher.match_arithmetic("hello world")
        assert result is None
    
    def test_assignment_patterns(self):
        """Test assignment pattern matching"""
        matcher = PatternMatcher()
        
        result = matcher.match_assignment("set x to 5")
        assert result is not None
        assert result[0] == "assign"
        assert "x" in result[1] and "5" in result[1]
        
        result = matcher.match_assignment("create variable name with value hello")
        assert result is not None
        assert result[0] == "assign"
        
        # No match
        result = matcher.match_assignment("add x and y")
        assert result is None
    
    def test_conditional_patterns(self):
        """Test conditional pattern matching"""
        matcher = PatternMatcher()
        
        result = matcher.match_conditional("if x > 5 then print hello")
        assert result is not None
        assert result[0] == "conditional"
        
        result = matcher.match_conditional("when x equals 10 do something")
        assert result is not None
        assert result[0] == "conditional"
        
        # No match
        result = matcher.match_conditional("add x and y")
        assert result is None
    
    def test_loop_patterns(self):
        """Test loop pattern matching"""
        matcher = PatternMatcher()
        
        result = matcher.match_loop("repeat 5 times")
        assert result is not None
        assert result[0] == "repeat"
        
        result = matcher.match_loop("for each item in list")
        assert result is not None
        assert result[0] == "for_each"
        
        # No match
        result = matcher.match_loop("add x and y")
        assert result is None
    
    def test_data_operation_patterns(self):
        """Test data operation pattern matching"""
        matcher = PatternMatcher()
        
        result = matcher.match_data_operation("create list with items")
        assert result is not None
        assert result[0] == "create_list"
        
        result = matcher.match_data_operation("add item to list")
        assert result is not None
        assert result[0] == "append_list"
        
        # No match
        result = matcher.match_data_operation("add x and y")
        assert result is None


class TestInputParser:
    """Test cases for InputParser class"""
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        parser = InputParser()
        assert parser.pattern_matcher is not None
    
    def test_tokenize_input(self):
        """Test input tokenization"""
        parser = InputParser()
        
        tokens = parser.tokenize_input("add x and 5")
        assert len(tokens) > 0
        
        # Check token types
        token_texts = [token.text for token in tokens]
        assert "add" in token_texts
        assert "x" in token_texts
        assert "5" in token_texts
        
        # Check number classification
        number_tokens = [token for token in tokens if token.token_type == TokenType.NUMBER]
        assert len(number_tokens) > 0
        assert "5" in [token.text for token in number_tokens]
    
    def test_identify_pattern_arithmetic(self):
        """Test arithmetic pattern identification"""
        parser = InputParser()
        
        assert parser.identify_pattern("add x and y") == PatternType.ARITHMETIC
        assert parser.identify_pattern("multiply a by b") == PatternType.ARITHMETIC
        assert parser.identify_pattern("calculate 5 plus 3") == PatternType.ARITHMETIC
    
    def test_identify_pattern_assignment(self):
        """Test assignment pattern identification"""
        parser = InputParser()
        
        assert parser.identify_pattern("set x to 5") == PatternType.ASSIGNMENT
        assert parser.identify_pattern("create variable name with value hello") == PatternType.ASSIGNMENT
    
    def test_identify_pattern_conditional(self):
        """Test conditional pattern identification"""
        parser = InputParser()
        
        assert parser.identify_pattern("if x > 5 then print hello") == PatternType.CONDITIONAL
        assert parser.identify_pattern("when x equals 10 do something") == PatternType.CONDITIONAL
    
    def test_identify_pattern_loop(self):
        """Test loop pattern identification"""
        parser = InputParser()
        
        assert parser.identify_pattern("repeat 5 times") == PatternType.LOOP
        assert parser.identify_pattern("for each item in list") == PatternType.LOOP
    
    def test_identify_pattern_data_operation(self):
        """Test data operation pattern identification"""
        parser = InputParser()
        
        assert parser.identify_pattern("create list with items") == PatternType.DATA_OPERATION
        assert parser.identify_pattern("add item to list") == PatternType.DATA_OPERATION
    
    def test_identify_pattern_unknown(self):
        """Test unknown pattern identification"""
        parser = InputParser()
        
        assert parser.identify_pattern("hello world") == PatternType.UNKNOWN
        assert parser.identify_pattern("random text here") == PatternType.UNKNOWN
    
    def test_extract_variables(self):
        """Test variable extraction"""
        parser = InputParser()
        
        # Test number extraction
        variables = parser.extract_variables("add x and 5")
        # Check that we have both variable names and numbers
        var_names = [k for k, v in variables.items() if v is None]  # Variables with unknown values
        number_vars = [k for k, v in variables.items() if isinstance(v, int)]
        assert "x" in var_names or "x" in variables  # x should be extracted as variable
        assert len(number_vars) > 0  # Should have at least one number
        
        # Test string extraction
        variables = parser.extract_variables('set name to "hello"')
        string_vars = [k for k, v in variables.items() if isinstance(v, str)]
        assert len(string_vars) > 0
        
        # Test variable name extraction
        variables = parser.extract_variables("multiply width by height")
        assert "width" in variables
        assert "height" in variables
    
    def test_parse_sentence_arithmetic(self):
        """Test parsing arithmetic sentences"""
        parser = InputParser()
        
        parsed = parser.parse_sentence("add x and y")
        
        assert parsed.original_text == "add x and y"
        assert parsed.pattern_type == PatternType.ARITHMETIC
        assert len(parsed.operations) > 0
        assert parsed.operations[0].operation_type == "add"
        assert "x" in parsed.operations[0].operands
        assert "y" in parsed.operations[0].operands
    
    def test_parse_sentence_assignment(self):
        """Test parsing assignment sentences"""
        parser = InputParser()
        
        parsed = parser.parse_sentence("set x to 5")
        
        assert parsed.original_text == "set x to 5"
        assert parsed.pattern_type == PatternType.ASSIGNMENT
        assert len(parsed.operations) > 0
        assert parsed.operations[0].operation_type == "assign"
        assert parsed.operations[0].result_variable == "x"
    
    def test_parse_sentence_conditional(self):
        """Test parsing conditional sentences"""
        parser = InputParser()
        
        parsed = parser.parse_sentence("if x > 5 then print hello")
        
        assert parsed.original_text == "if x > 5 then print hello"
        assert parsed.pattern_type == PatternType.CONDITIONAL
        assert len(parsed.conditions) > 0
        assert "x > 5" in parsed.conditions[0].condition_text
    
    def test_parse_sentence_data_operation(self):
        """Test parsing data operation sentences"""
        parser = InputParser()
        
        parsed = parser.parse_sentence("create list with items")
        
        assert parsed.original_text == "create list with items"
        assert parsed.pattern_type == PatternType.DATA_OPERATION
        assert len(parsed.operations) > 0
        assert parsed.operations[0].operation_type == "create"
    
    def test_parse_sentence_with_metadata(self):
        """Test that parsed sentences include metadata"""
        parser = InputParser()
        
        parsed = parser.parse_sentence("add x and y")
        
        assert "tokens" in parsed.metadata
        assert "confidence" in parsed.metadata
        assert isinstance(parsed.metadata["confidence"], float)
        assert 0.0 <= parsed.metadata["confidence"] <= 1.0
    
    def test_validate_input_valid(self):
        """Test input validation for valid inputs"""
        parser = InputParser()
        
        valid, message = parser.validate_input("add x and y")
        assert valid is True
        assert message == "Input is valid"
        
        valid, message = parser.validate_input("set variable to 5")
        assert valid is True
    
    def test_validate_input_invalid(self):
        """Test input validation for invalid inputs"""
        parser = InputParser()
        
        # Empty input
        valid, message = parser.validate_input("")
        assert valid is False
        assert "empty" in message.lower()
        
        # Whitespace only
        valid, message = parser.validate_input("   ")
        assert valid is False
        assert "whitespace" in message.lower()
        
        # Too short
        valid, message = parser.validate_input("hi")
        assert valid is False
        assert "short" in message.lower()
        
        # Too long
        valid, message = parser.validate_input("x" * 1001)
        assert valid is False
        assert "long" in message.lower()
        
        # Dangerous content
        valid, message = parser.validate_input("import os")
        assert valid is False
        assert "unsafe" in message.lower()
    
    def test_parse_sentence_empty_input(self):
        """Test parsing empty input raises error"""
        parser = InputParser()
        
        with pytest.raises(ValueError, match="Input sentence cannot be empty"):
            parser.parse_sentence("")
        
        with pytest.raises(ValueError, match="Input sentence cannot be empty"):
            parser.parse_sentence("   ")
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        parser = InputParser()
        
        # Known pattern should have higher confidence
        parsed_known = parser.parse_sentence("add x and y")
        assert parsed_known.metadata["confidence"] > 0.5
        
        # Unknown pattern should have lower confidence
        parsed_unknown = parser.parse_sentence("random text here")
        assert parsed_unknown.metadata["confidence"] < 0.5
    
    def test_complex_sentence_parsing(self):
        """Test parsing more complex sentences"""
        parser = InputParser()
        
        # Complex arithmetic
        parsed = parser.parse_sentence("calculate the sum of width and height")
        assert parsed.pattern_type == PatternType.ARITHMETIC
        
        # Assignment with expression
        parsed = parser.parse_sentence("set result to the value 42")
        assert parsed.pattern_type == PatternType.ASSIGNMENT
        
        # Data operation with details
        parsed = parser.parse_sentence("create a list with values 1, 2, 3")
        assert parsed.pattern_type == PatternType.DATA_OPERATION
    
    def test_case_insensitive_parsing(self):
        """Test that parsing is case insensitive"""
        parser = InputParser()
        
        # Test different cases
        parsed1 = parser.parse_sentence("ADD X AND Y")
        parsed2 = parser.parse_sentence("add x and y")
        parsed3 = parser.parse_sentence("Add X And Y")
        
        assert parsed1.pattern_type == PatternType.ARITHMETIC
        assert parsed2.pattern_type == PatternType.ARITHMETIC
        assert parsed3.pattern_type == PatternType.ARITHMETIC
    
    def test_variable_extraction_edge_cases(self):
        """Test variable extraction with edge cases"""
        parser = InputParser()
        
        # Multiple numbers
        variables = parser.extract_variables("add 5 and 10 then multiply by 2")
        number_vars = [v for v in variables.values() if isinstance(v, (int, float))]
        assert len(number_vars) >= 3
        
        # Floating point numbers
        variables = parser.extract_variables("set pi to 3.14")
        float_vars = [v for v in variables.values() if isinstance(v, float)]
        assert len(float_vars) > 0
        
        # Mixed content
        variables = parser.extract_variables('create user with name "John" and age 25')
        assert len(variables) > 0