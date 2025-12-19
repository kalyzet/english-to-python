"""
Input Parser component for English to Python Translator
Menganalisis dan memparse kalimat bahasa Inggris menjadi struktur data
"""

import re
import nltk
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

try:
    from ..models import ParsedSentence, Operation, Condition, PatternType
except (ImportError, ValueError):
    # Fallback for when running tests or direct imports
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    parent_dir = os.path.dirname(src_dir)
    
    for path in [src_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    try:
        from models import ParsedSentence, Operation, Condition, PatternType
    except ImportError:
        import src.models.parsed_sentence as ps
        ParsedSentence = ps.ParsedSentence
        Operation = ps.Operation
        Condition = ps.Condition
        PatternType = ps.PatternType


class TokenType(Enum):
    """Types of tokens that can be identified in English sentences"""
    VERB = "verb"
    NOUN = "noun"
    NUMBER = "number"
    VARIABLE = "variable"
    OPERATOR = "operator"
    CONDITION = "condition"
    KEYWORD = "keyword"


@dataclass
class Token:
    """Represents a token in the parsed sentence"""
    text: str
    token_type: TokenType
    position: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PatternMatcher:
    """Handles pattern matching for different types of English constructs"""
    
    def __init__(self):
        self._arithmetic_patterns = [
            # Division patterns (check first to avoid conflicts)
            (r'\bdivide\s+(\w+)\s+by\s+(\w+)', 'divide'),
            (r'\b(\w+)\s+divided\s+by\s+(\w+)', 'divide'),
            (r'\b(?:split)\s+(\w+)\s+(?:by|with|/)\s+(\w+)', 'divide'),
            (r'\b(\w+)\s*/\s*(\w+)', 'divide'),
            (r'\bcalculate\s+(\w+)\s+divided\s+by\s+(\w+)', 'divide'),
            
            # Addition patterns
            (r'\b(?:add|plus|sum)\s+(\w+)\s+(?:and|with|\+)\s+(\w+)', 'add'),
            (r'\b(\w+)\s+plus\s+(\w+)', 'add'),
            (r'\b(\w+)\s*\+\s*(\w+)', 'add'),
            (r'\bcalculate\s+(\w+)\s+plus\s+(\w+)', 'add'),
            (r'\bcalculate\s+(?:the\s+)?sum\s+of\s+(\w+)\s+and\s+(\w+)', 'add'),
            
            # Subtraction patterns
            (r'\b(?:subtract|minus)\s+(\w+)\s+(?:from|and)\s+(\w+)', 'subtract'),
            (r'\b(\w+)\s+minus\s+(\w+)', 'subtract'),
            (r'\b(\w+)\s*-\s*(\w+)', 'subtract'),
            (r'\bcalculate\s+(\w+)\s+minus\s+(\w+)', 'subtract'),
            
            # Multiplication patterns (check after division to avoid conflicts)
            (r'\bmultiply\s+(\w+)\s+(?:by|and|\*)\s+(\w+)', 'multiply'),
            (r'\b(\w+)\s+times\s+(\w+)', 'multiply'),
            (r'\b(\w+)\s*\*\s*(\w+)', 'multiply'),
            (r'\bcalculate\s+(\w+)\s+times\s+(\w+)', 'multiply'),
        ]
        
        self._assignment_patterns = [
            (r'\bset\s+(\w+)\s+to\s+(.+)', 'assign'),
            (r'\bcreate\s+variable\s+(\w+)\s+with\s+value\s+(.+)', 'assign'),
            # More specific assignment pattern - avoid matching arithmetic expressions
            (r'\b([a-zA-Z_]\w*)\s*=\s*([^+\-*/=<>!]+)', 'assign'),
            (r'\bassign\s+(.+)\s+to\s+(\w+)', 'assign'),
        ]
        
        self._conditional_patterns = [
            (r'\bif\s+(.+?)\s+then\s+(.+?)(?:\s+else\s+(.+))?', 'conditional'),
            (r'\bwhen\s+(.+?)\s+then\s+(.+)', 'conditional'),
            (r'\bwhen\s+(.+?)\s+do\s+(.+)', 'conditional'),
            (r'\bunless\s+(.+?)\s+then\s+(.+)', 'conditional'),
        ]
        
        self._loop_patterns = [
            (r'\brepeat\s+(\d+)\s+times?\s*:?\s*(.+)?', 'repeat'),
            (r'\bloop\s+through\s+(\w+)', 'loop_through'),
            (r'\bloop\s+(.+)', 'loop'),
            (r'\bfor\s+each\s+(\w+)\s+in\s+(\w+)\s*:?\s*(.+)?', 'for_each'),
            (r'\bwhile\s+(.+?)\s*:?\s*(.+)?', 'while'),
        ]
        
        self._data_operation_patterns = [
            (r'\bcreate\s+(?:a\s+)?list(?:\s+with\s+(.+))?', 'create_list'),
            (r'\bcreate\s+list(?:\s+with\s+(.+))?', 'create_list'),  # Handle "create list" without "a"
            (r'\bmake\s+(?:a\s+)?list', 'create_list'),
            (r'\bnew\s+list', 'create_list'),
            (r'\bcreate\s+(?:a\s+)?(?:dictionary|dict)(?:\s+with\s+(.+))?', 'create_dict'),
            (r'\bcreate\s+(?:dictionary|dict)(?:\s+with\s+(.+))?', 'create_dict'),  # Handle without "a"
            (r'\bmake\s+(?:a\s+)?(?:dictionary|dict)', 'create_dict'),
            (r'\bnew\s+(?:dictionary|dict)', 'create_dict'),
            (r'\badd\s+(.+?)\s+(?:to|from)\s+(?:list\s+)?(\w+)', 'append_list'),
            (r'\bremove\s+(.+?)\s+(?:from|to)\s+(?:list\s+)?(\w+)', 'remove_list'),
            (r'\bget\s+(.+?)\s+from\s+(?:list\s+)?(\w+)', 'get_item'),
        ]
    
    def match_arithmetic(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Match arithmetic patterns in text"""
        for pattern, operation in self._arithmetic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return operation, list(match.groups())
        return None
    
    def match_assignment(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Match assignment patterns in text"""
        for pattern, operation in self._assignment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return operation, list(match.groups())
        return None
    
    def match_conditional(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Match conditional patterns in text"""
        for pattern, operation in self._conditional_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return operation, list(match.groups())
        return None
    
    def match_loop(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Match loop patterns in text"""
        for pattern, operation in self._loop_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return operation, list(match.groups())
        return None
    
    def match_data_operation(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Match data operation patterns in text"""
        for pattern, operation in self._data_operation_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return operation, list(match.groups())
        return None


class InputParser:
    """
    Main Input Parser class for analyzing and parsing English sentences
    """
    
    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Ensure required NLTK data is available"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
            except Exception:
                pass  # Continue without NLTK if download fails
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            try:
                nltk.download('averaged_perceptron_tagger', quiet=True)
            except Exception:
                pass  # Continue without NLTK if download fails
    
    def tokenize_input(self, sentence: str) -> List[Token]:
        """
        Tokenize input sentence into meaningful tokens
        """
        tokens = []
        
        # Basic tokenization - split by whitespace and punctuation
        words = re.findall(r'\b\w+\b|\d+|[^\w\s]', sentence.lower())
        
        for i, word in enumerate(words):
            token_type = self._classify_token(word)
            token = Token(
                text=word,
                token_type=token_type,
                position=i
            )
            tokens.append(token)
        
        return tokens
    
    def _classify_token(self, word: str) -> TokenType:
        """Classify a word into a token type"""
        # Numbers
        if re.match(r'^\d+(\.\d+)?$', word):
            return TokenType.NUMBER
        
        # Operators
        if word in ['+', '-', '*', '/', '=', '>', '<', '>=', '<=', '==', '!=']:
            return TokenType.OPERATOR
        
        # Keywords
        keywords = {
            'add', 'subtract', 'multiply', 'divide', 'plus', 'minus', 'times',
            'if', 'then', 'else', 'when', 'do', 'while', 'for', 'each', 'in',
            'repeat', 'create', 'set', 'assign', 'to', 'with', 'value',
            'list', 'dictionary', 'dict', 'get', 'from', 'remove'
        }
        if word in keywords:
            return TokenType.KEYWORD
        
        # Conditions
        condition_words = {'greater', 'less', 'equal', 'than', 'not'}
        if word in condition_words:
            return TokenType.CONDITION
        
        # Variables (default for other words)
        return TokenType.VARIABLE
    
    def identify_pattern(self, sentence: str) -> PatternType:
        """
        Identify the main pattern type of the sentence
        """
        sentence_lower = sentence.lower()
        
        # Check for conditional patterns first (they often contain other keywords)
        if self.pattern_matcher.match_conditional(sentence_lower):
            return PatternType.CONDITIONAL
        
        # Check for loop patterns
        if self.pattern_matcher.match_loop(sentence_lower):
            return PatternType.LOOP
        
        # Check for data operation patterns before assignment (to handle "add X to list Y")
        if self.pattern_matcher.match_data_operation(sentence_lower):
            return PatternType.DATA_OPERATION
        
        # Check for assignment patterns
        if self.pattern_matcher.match_assignment(sentence_lower):
            return PatternType.ASSIGNMENT
        
        # Check for arithmetic patterns last (they have broad patterns)
        if self.pattern_matcher.match_arithmetic(sentence_lower):
            return PatternType.ARITHMETIC
        
        return PatternType.UNKNOWN
    
    def extract_variables(self, sentence: str) -> Dict[str, Any]:
        """
        Extract variable names and values from the sentence
        """
        variables = {}
        
        # Extract numbers as potential variable values
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', sentence)
        for i, num in enumerate(numbers):
            if '.' in num:
                variables[f'num_{i}'] = float(num)
            else:
                variables[f'num_{i}'] = int(num)
        
        # Extract quoted strings as potential values
        strings = re.findall(r'"([^"]*)"', sentence)
        for i, string in enumerate(strings):
            variables[f'str_{i}'] = string
        
        # Extract variable names (words that look like identifiers)
        var_names = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', sentence)
        keywords = {
            'add', 'subtract', 'multiply', 'divide', 'plus', 'minus', 'times',
            'if', 'then', 'else', 'when', 'do', 'while', 'for', 'each', 'in',
            'repeat', 'create', 'set', 'assign', 'to', 'with', 'value',
            'list', 'dictionary', 'dict', 'get', 'from', 'remove', 'and', 'or'
        }
        
        for name in var_names:
            if name.lower() not in keywords and len(name) >= 1:  # Allow single character variables
                if name not in variables:
                    variables[name] = None  # Variable exists but value unknown
        
        return variables
    
    def _parse_arithmetic_operation(self, sentence: str) -> List[Operation]:
        """Parse arithmetic operations from sentence"""
        operations = []
        match_result = self.pattern_matcher.match_arithmetic(sentence)
        
        if match_result:
            operation_type, operands = match_result
            
            # Clean operands
            cleaned_operands = []
            for operand in operands:
                operand = operand.strip()
                if operand:
                    cleaned_operands.append(operand)
            
            if len(cleaned_operands) >= 2:
                operation = Operation(
                    operation_type=operation_type,
                    operands=cleaned_operands[:2],
                    result_variable="result"
                )
                operations.append(operation)
        
        return operations
    
    def _parse_assignment_operation(self, sentence: str) -> List[Operation]:
        """Parse assignment operations from sentence"""
        operations = []
        match_result = self.pattern_matcher.match_assignment(sentence)
        
        if match_result:
            operation_type, parts = match_result
            
            if len(parts) >= 2:
                var_name = parts[0].strip()
                value = parts[1].strip()
                
                operation = Operation(
                    operation_type="assign",
                    operands=[value],
                    result_variable=var_name
                )
                operations.append(operation)
        
        return operations
    
    def _parse_data_operation(self, sentence: str) -> List[Operation]:
        """Parse data structure operations from sentence"""
        operations = []
        match_result = self.pattern_matcher.match_data_operation(sentence)
        
        if match_result:
            operation_type, parts = match_result
            
            if operation_type in ['create_list', 'create_dict']:
                # Handle cases where parts might be [None] or empty
                items = ""
                if parts and parts[0] is not None:
                    items = parts[0].strip()
                
                data_type = 'list' if operation_type == 'create_list' else 'dict'
                result_var = 'new_list' if data_type == 'list' else 'new_dict'
                
                operation = Operation(
                    operation_type="create",
                    operands=[items] if items else [],
                    result_variable=result_var
                )
                operations.append(operation)
            
            elif operation_type in ['append_list', 'remove_list']:
                if len(parts) >= 2:
                    item = parts[0].strip()
                    list_name = parts[1].strip()
                    op_type = "append" if operation_type == 'append_list' else "remove"
                    
                    operation = Operation(
                        operation_type=op_type,
                        operands=[item, list_name],
                        result_variable=list_name
                    )
                    operations.append(operation)
        
        return operations
    
    def _parse_conditions(self, sentence: str) -> List[Condition]:
        """Parse conditional statements from sentence"""
        conditions = []
        match_result = self.pattern_matcher.match_conditional(sentence)
        
        if match_result:
            condition_type, parts = match_result
            
            if parts and parts[0]:
                condition_text = parts[0].strip()
                variables_used = self._extract_variables_from_condition(condition_text)
                
                condition = Condition(
                    condition_text=condition_text,
                    condition_type="if",
                    variables_used=variables_used
                )
                conditions.append(condition)
        
        return conditions
    
    def _extract_variables_from_condition(self, condition_text: str) -> List[str]:
        """Extract variable names from condition text"""
        variables = []
        var_names = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', condition_text)
        
        keywords = {'and', 'or', 'not', 'is', 'than', 'equal', 'greater', 'less'}
        for name in var_names:
            if name.lower() not in keywords:
                variables.append(name)
        
        return variables
    
    def parse_sentence(self, sentence: str) -> ParsedSentence:
        """
        Main method to parse an English sentence into a ParsedSentence object
        """
        if not sentence or not sentence.strip():
            raise ValueError("Input sentence cannot be empty")
        
        # Create parsed sentence object
        parsed = ParsedSentence(
            original_text=sentence.strip(),
            pattern_type=self.identify_pattern(sentence)
        )
        
        # Extract variables
        variables = self.extract_variables(sentence)
        for name, value in variables.items():
            parsed.add_variable(name, value)
        
        # Parse operations based on pattern type
        if parsed.pattern_type == PatternType.ARITHMETIC:
            operations = self._parse_arithmetic_operation(sentence)
            for op in operations:
                parsed.add_operation(op)
        
        elif parsed.pattern_type == PatternType.ASSIGNMENT:
            operations = self._parse_assignment_operation(sentence)
            for op in operations:
                parsed.add_operation(op)
        
        elif parsed.pattern_type == PatternType.DATA_OPERATION:
            operations = self._parse_data_operation(sentence)
            for op in operations:
                parsed.add_operation(op)
        
        elif parsed.pattern_type == PatternType.CONDITIONAL:
            conditions = self._parse_conditions(sentence)
            for cond in conditions:
                parsed.add_condition(cond)
        
        # Add metadata
        parsed.metadata['tokens'] = len(self.tokenize_input(sentence))
        parsed.metadata['confidence'] = self._calculate_confidence(parsed)
        
        return parsed
    
    def _calculate_confidence(self, parsed: ParsedSentence) -> float:
        """Calculate confidence score for the parsing result"""
        confidence = 0.0
        
        # Base confidence for known patterns
        if parsed.pattern_type != PatternType.UNKNOWN:
            confidence += 0.5
        
        # Bonus for having operations or conditions
        if len(parsed.operations) > 0:
            confidence += 0.3
        
        if len(parsed.conditions) > 0:
            confidence += 0.3
        
        # Bonus for having variables
        if len(parsed.variables) > 0:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def validate_input(self, sentence: str) -> Tuple[bool, str]:
        """
        Validate input sentence for basic requirements
        """
        if not sentence:
            return False, "Input cannot be empty"
        
        if not sentence.strip():
            return False, "Input cannot be only whitespace"
        
        if len(sentence.strip()) < 3:
            return False, "Input too short to be meaningful"
        
        if len(sentence) > 1000:
            return False, "Input too long (max 1000 characters)"
        
        # Check for potentially dangerous content
        dangerous_patterns = [
            r'\bimport\s+os\b',
            r'\bexec\b',  # Match exec with or without parentheses
            r'\beval\b',  # Match eval with or without parentheses
            r'\b__.*__\b',
            r'\bopen\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return False, "Input contains potentially unsafe content"
        
        return True, "Input is valid"