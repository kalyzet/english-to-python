"""
Input Parser component for English to Python Translator
Menganalisis dan memparse kalimat bahasa Inggris menjadi struktur data
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .parsed_sentence import ParsedSentence, Operation, Condition, PatternType
from .literals import format_literal, format_index


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
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class PatternMatcher:
    """Handles pattern matching for different types of English constructs"""
    
    def __init__(self) -> None:
        # Operand: decimal number ("0.1") or word/identifier ("total", "x")
        op = r'(\d+(?:\.\d+)?|\w+)'
        self._arithmetic_patterns = [
            # Division patterns (check first to avoid conflicts)
            (rf'\bdivide\s+{op}\s+by\s+{op}', 'divide'),
            (rf'\b{op}\s+divided\s+by\s+{op}', 'divide'),
            (rf'\b(?:split)\s+{op}\s+(?:by|with|/)\s+{op}', 'divide'),
            (rf'\b{op}\s*/\s*{op}', 'divide'),
            (rf'\bcalculate\s+{op}\s+divided\s+by\s+{op}', 'divide'),
            
            # Addition patterns
            (rf'\b(?:add|plus|sum)\s+{op}\s+(?:and|with|\+)\s+{op}', 'add'),
            (rf'\b{op}\s+plus\s+{op}', 'add'),
            (rf'\b{op}\s*\+\s*{op}', 'add'),
            (rf'\bcalculate\s+{op}\s+plus\s+{op}', 'add'),
            (rf'\bcalculate\s+(?:the\s+)?sum\s+of\s+{op}\s+and\s+{op}', 'add'),
            
            # Subtraction patterns
            (rf'\b(?:subtract|minus)\s+{op}\s+(?:from|and)\s+{op}', 'subtract'),
            (rf'\b{op}\s+minus\s+{op}', 'subtract'),
            (rf'\b{op}\s*-\s*{op}', 'subtract'),
            (rf'\bcalculate\s+{op}\s+minus\s+{op}', 'subtract'),
            
            # Multiplication patterns (check after division to avoid conflicts)
            (rf'\bmultiply\s+{op}\s+(?:by|and|\*)\s+{op}', 'multiply'),
            (rf'\b{op}\s+times\s+{op}', 'multiply'),
            (rf'\b{op}\s*\*\s*{op}', 'multiply'),
            (rf'\bcalculate\s+{op}\s+times\s+{op}', 'multiply'),
        ]
        
        self._assignment_patterns = [
            (r'\bset\s+(\w+)\s+to\s+(.+)', 'assign'),
            (r'\bcreate\s+variable\s+(\w+)\s+with\s+value\s+(.+)', 'assign'),
            # More specific assignment pattern - avoid matching arithmetic expressions
            (r'\b([a-zA-Z_]\w*)\s*=\s*([^+\-*/=<>!]+)', 'assign'),
            # Value first, variable second: "assign 42 to answer"
            (r'\bassign\s+(.+)\s+to\s+(\w+)', 'assign_to'),
        ]
        
        self._conditional_patterns = [
            # Pattern with else clause - must come first
            (r'\bif\s+(.+?)\s+then\s+(.+?)\s+else\s+(.+)$', 'conditional'),
            # Pattern without else clause
            (r'\bif\s+(.+?)\s+then\s+(.+)$', 'conditional'),
            (r'\bwhen\s+(.+?)\s+then\s+(.+)$', 'conditional'),
            (r'\bwhen\s+(.+?)\s+do\s+(.+)$', 'conditional'),
            (r'\bunless\s+(.+?)\s+then\s+(.+)$', 'conditional'),
        ]
        
        # Loop statements must start the sentence (anchored) so that words like
        # "while"/"loop" appearing as data ("add while to list a") stay data ops.
        self._loop_patterns = [
            (r'\A\s*repeat\s+(\d+)\s+times?\s*:?\s*(.+)?', 'repeat'),
            (r'\A\s*loop\s+through\s+(\w+)', 'loop_through'),
            (r'\A\s*loop\s+(.+)', 'loop'),
            (r'\A\s*for\s+each\s+(\w+)\s+in\s+(\w+)\s*:?\s*(.+)?', 'for_each'),
            (r'\A\s*while\s+(.+?)\s*:?\s*(.+)?', 'while'),
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
    
    # Words treated as variables when printing (avoids accidental NameError)
    COMMON_VARS = {
        'age', 'score', 'temperature', 'humidity', 'count',
        'total', 'result', 'status', 'level', 'lives', 'name',
    }
    
    # Action keywords that start a loop/branch body after a condition
    ACTION_KEYWORDS_RE = re.compile(
        r'\b(print|set|increment|decrement|add|subtract|multiply|divide|create|remove|get)\b',
        re.IGNORECASE,
    )
    
    def __init__(self) -> None:
        self.pattern_matcher = PatternMatcher()
    
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
    
    def starts_with_control_structure(self, text: str) -> bool:
        """
        True when a conditional or loop pattern begins at the very start of the
        text (so the rest of the line belongs to that statement, not a new one).
        """
        text_lower = text.lower()
        patterns = (
            self.pattern_matcher._conditional_patterns
            + self.pattern_matcher._loop_patterns
        )
        for pattern, _operation in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if match and match.start() == 0:
                return True
        return False
    
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
    
    def extract_variables(self, sentence: str, pattern_type: Optional[PatternType] = None) -> Dict[str, Any]:
        """
        Extract variable names and values from the sentence
        """
        variables: Dict[str, Any] = {}
        
        # For assignment patterns, don't extract any variables
        # since the assignment operation will handle everything
        if pattern_type == PatternType.ASSIGNMENT:
            return variables
        
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
            
            # "subtract X from Y" means Y - X, so reverse the captured groups
            if operation_type == 'subtract':
                from_match = re.search(
                    r'\bsubtract\s+(\d+(?:\.\d+)?|\w+)\s+from\s+(\d+(?:\.\d+)?|\w+)',
                    sentence, re.IGNORECASE
                )
                if from_match:
                    operands = [from_match.group(2), from_match.group(1)]
            
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
                if operation_type == 'assign_to':
                    # "assign VALUE to VARIABLE" captures value first
                    value, var_name = parts[0], parts[1]
                else:
                    var_name, value = parts[0], parts[1]
                
                var_name = var_name.strip()
                value = value.strip()
                
                # Format the value properly for Python
                formatted_value = self._format_assignment_value(value)
                
                operation = Operation(
                    operation_type="assign",
                    operands=[formatted_value],
                    result_variable=var_name
                )
                operations.append(operation)
        
        return operations
    
    @staticmethod
    def _split_items(items: str) -> List[str]:
        """Split a comma/and separated item list into individual raw items"""
        if not items:
            return []
        parts = re.split(r'\s*,\s*|\s+and\s+', items)
        return [part.strip() for part in parts if part.strip()]
    
    def _format_dict_entries(self, items: str) -> List[str]:
        """Turn 'name John and age 25' into ['\"name\": \"John\"', '\"age\": 25']"""
        entries = []
        for part in self._split_items(items):
            key_value = part.split(None, 1)
            key = key_value[0].rstrip(':,')
            if len(key_value) == 2 and key_value[1].strip():
                value = self._format_assignment_value(key_value[1].strip())
            else:
                value = '""'
            entries.append(f'"{key}": {value}')
        return entries
    
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
                
                if data_type == 'dict':
                    operands = self._format_dict_entries(items)
                else:
                    operands = self._split_items(items)
                
                operation = Operation(
                    operation_type="create",
                    operands=operands,
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
                        operands=[list_name, item],
                        result_variable=list_name
                    )
                    operations.append(operation)
            
            elif operation_type == 'get_item':
                if len(parts) >= 2:
                    key = parts[0].strip()
                    list_name = parts[1].strip()
                    operation = Operation(
                        operation_type="get",
                        operands=[list_name, key],
                        result_variable="result"
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
    
    def _format_action(
        self,
        action_text: str,
        known_vars: Optional[List[str]] = None,
        unrecognized: Optional[List[str]] = None,
    ) -> str:
        """Format action text to valid Python code that can be executed"""
        action = action_text.strip()
        if not action:
            return 'pass'
        
        known = {var for var in (known_vars or []) if var}
        
        def _record_unrecognized() -> str:
            if unrecognized is not None:
                unrecognized.append(action)
            return 'pass'
        
        action_lower = action.lower()
        
        # Handle print statements
        if action_lower == 'print':
            return 'print()'
        if action_lower.startswith('print '):
            print_content = action[6:].strip()
            if not print_content:
                return 'print()'
            
            # Already-quoted string: print("hello world")
            if ((print_content.startswith('"') and print_content.endswith('"')) or
                    (print_content.startswith("'") and print_content.endswith("'"))):
                return f'print({print_content})'
            
            # Known variables are printed directly, everything else is a string
            if print_content.isidentifier():
                if print_content in known or print_content in self.COMMON_VARS:
                    return f'print({print_content})'
                return f'print("{print_content}")'
            
            return f'print("{print_content}")'
        
        # Handle assignment within a branch: "set x to 10"
        if action_lower.startswith('set '):
            operations = self._parse_assignment_operation(action)
            if operations and operations[0].result_variable and operations[0].operands:
                operation = operations[0]
                return f'{operation.result_variable} = {operation.operands[0]}'
            return _record_unrecognized()
        
        # increment / decrement
        increment_match = re.match(r'^(increment|decrement)\s+(\w+)$', action, re.IGNORECASE)
        if increment_match:
            operator = '+=' if increment_match.group(1).lower() == 'increment' else '-='
            return f'{increment_match.group(2)} {operator} 1'
        
        # Arithmetic action: "add 1 and 2" / "multiply x by 2"
        arithmetic_ops = self._parse_arithmetic_operation(action)
        if arithmetic_ops:
            operation = arithmetic_ops[0]
            if len(operation.operands) >= 2:
                operator = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/'}[
                    operation.operation_type
                ]
                result = operation.result_variable or 'result'
                return f'{result} = {operation.operands[0]} {operator} {operation.operands[1]}'
        
        # Data action: "add x to my_list" / "remove x from my_list" / "get x from list"
        data_ops = self._parse_data_operation(action)
        if data_ops:
            rendered = self._render_data_operation(data_ops[0])
            if rendered is not None:
                return rendered
        
        # Unrecognized action
        return _record_unrecognized()
    
    def _render_data_operation(self, operation: Operation) -> Optional[str]:
        """Render a single data operation as one line of Python code"""
        if operation.operation_type == 'append' and len(operation.operands) >= 2:
            list_var, item = operation.operands[0], operation.operands[1]
            return f'{list_var}.append({format_literal(item)})'
        if operation.operation_type == 'remove' and len(operation.operands) >= 2:
            list_var, item = operation.operands[0], operation.operands[1]
            return f'{list_var}.remove({format_literal(item)})'
        if operation.operation_type == 'get' and len(operation.operands) >= 2:
            list_var, key = operation.operands[0], operation.operands[1]
            result = operation.result_variable or 'result'
            return f'{result} = {list_var}[{format_index(key)}]'
        return None
    
    def _format_assignment_value(self, value: str) -> str:
        """Format assignment value to proper Python syntax"""
        value = value.strip()
        
        # Check if it's a number
        try:
            # Try integer first
            int(value)
            return value
        except ValueError:
            try:
                # Try float
                float(value)
                return value
            except ValueError:
                pass
        
        # Check if it's a boolean
        if value.lower() in ['true', 'false']:
            return value.capitalize()
        
        # Check if it's None
        if value.lower() == 'none':
            return 'None'
        
        # Check if it's already quoted
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            return value
        
        # For everything else, treat as string
        return f'"{value}"'
    
    def _parse_loop(self, sentence: str, parsed: ParsedSentence) -> None:
        """Parse loop statements and fill loop metadata for the code generator"""
        match_result = self.pattern_matcher.match_loop(sentence)
        if not match_result:
            return
        
        operation, _parts = match_result
        unrecognized: List[str] = []
        known_vars: List[str] = []
        body_text = ''
        
        if operation == 'repeat':
            repeat_match = re.search(
                r'\brepeat\s+(\d+)\s+times?\s*:?\s*(.*)$', sentence,
                re.IGNORECASE | re.DOTALL,
            )
            if not repeat_match:
                raise ValueError("Could not parse repeat count")
            parsed.metadata['loop_type'] = 'repeat'
            parsed.metadata['count'] = repeat_match.group(1)
            body_text = repeat_match.group(2).strip()
        
        elif operation == 'for_each':
            for_match = re.search(
                r'\bfor\s+each\s+(\w+)\s+in\s+(\w+)\s*:?\s*(.*)$', sentence,
                re.IGNORECASE | re.DOTALL,
            )
            if not for_match:
                raise ValueError("Could not parse for-each loop")
            item = for_match.group(1)
            parsed.metadata['loop_type'] = 'for_each'
            parsed.metadata['item'] = item
            parsed.metadata['collection'] = for_match.group(2)
            body_text = for_match.group(3).strip()
            known_vars = [item]
        
        elif operation == 'loop_through':
            through_match = re.search(
                r'\bloop\s+through\s+(\w+)\s*:?\s*(.*)$', sentence,
                re.IGNORECASE | re.DOTALL,
            )
            if not through_match:
                raise ValueError("Could not parse loop collection")
            parsed.metadata['loop_type'] = 'for_each'
            parsed.metadata['item'] = 'item'
            parsed.metadata['collection'] = through_match.group(1)
            body_text = through_match.group(2).strip()
            known_vars = ['item']
        
        elif operation == 'while':
            rest = re.sub(r'^\s*while\s+', '', sentence, flags=re.IGNORECASE).strip()
            action_match = self.ACTION_KEYWORDS_RE.search(rest)
            if action_match:
                condition_text = rest[:action_match.start()].strip()
                # Drop the "do" separator between condition and action
                # (e.g. "x greater than 0 do print hi" -> condition "x greater than 0")
                condition_text = re.sub(
                    r'\s+do$', '', condition_text, flags=re.IGNORECASE
                ).strip()
                body_text = rest[action_match.start():].strip()
            else:
                do_match = re.search(r'\s+do\s+', rest, re.IGNORECASE)
                if do_match:
                    condition_text = rest[:do_match.start()].strip()
                    body_text = rest[do_match.end():].strip()
                else:
                    condition_text = rest
                    body_text = ''
            
            if not condition_text:
                raise ValueError("While loop requires a condition")
            
            parsed.add_condition(Condition(
                condition_text=condition_text,
                condition_type='while',
                variables_used=self._extract_variables_from_condition(condition_text),
            ))
            parsed.metadata['loop_type'] = 'while'
            known_vars = list(parsed.conditions[-1].variables_used)
        
        else:
            # Generic "loop <body>" is ambiguous
            raise ValueError(
                "Ambiguous 'loop' statement: use 'loop through <collection>', "
                "'repeat <N> times <action>', or 'while <condition> <action>'"
            )
        
        parsed.metadata['body'] = self._format_action(body_text, known_vars, unrecognized)
        if unrecognized:
            parsed.metadata['unrecognized_actions'] = unrecognized
    
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
        variables = self.extract_variables(sentence, parsed.pattern_type)
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
            match_result = self.pattern_matcher.match_data_operation(sentence)
            if match_result and match_result[0] in ('create_list', 'create_dict'):
                parsed.metadata['data_type'] = (
                    'list' if match_result[0] == 'create_list' else 'dict'
                )
            operations = self._parse_data_operation(sentence)
            for op in operations:
                parsed.add_operation(op)
        
        elif parsed.pattern_type == PatternType.CONDITIONAL:
            conditions = self._parse_conditions(sentence)
            for cond in conditions:
                parsed.add_condition(cond)
            
            known_vars: List[str] = []
            if conditions:
                known_vars = list(conditions[0].variables_used)
            unrecognized: List[str] = []
            
            # Extract action parts from conditional statement
            match_result = self.pattern_matcher.match_conditional(sentence)
            if match_result:
                _condition_type, parts = match_result
                if len(parts) >= 2 and parts[1]:
                    # Extract then_block action
                    then_action = parts[1].strip()
                    parsed.metadata['then_block'] = self._format_action(
                        then_action, known_vars, unrecognized
                    )
                
                if len(parts) >= 3 and parts[2]:
                    # Extract else_block action
                    else_action = parts[2].strip()
                    parsed.metadata['else_block'] = self._format_action(
                        else_action, known_vars, unrecognized
                    )
            
            if unrecognized:
                parsed.metadata['unrecognized_actions'] = unrecognized
        
        elif parsed.pattern_type == PatternType.LOOP:
            self._parse_loop(sentence, parsed)
        
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
            r'\bopen\b',  # File access, with or without parentheses
            r'\b__import__\b',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return False, "Input contains potentially unsafe content"
        
        return True, "Input is valid"