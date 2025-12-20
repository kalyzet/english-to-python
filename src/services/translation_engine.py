"""
Translation Engine service for English to Python Translator
Mengkoordinasi proses parsing dan code generation dengan error handling dan validation
"""

import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

try:
    from ..core.input_parser import InputParser
    from ..core.code_generator import CodeGenerator
    from ..models.parsed_sentence import ParsedSentence, PatternType
    from ..models.translation_result import TranslationResult
except (ImportError, ValueError):
    # Fallback for when running tests or direct imports
    import sys
    import os
    # Add both src and parent directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    parent_dir = os.path.dirname(src_dir)
    
    for path in [src_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    try:
        from core.input_parser import InputParser
        from core.code_generator import CodeGenerator
        from models.parsed_sentence import ParsedSentence, PatternType
        from models.translation_result import TranslationResult
    except ImportError:
        # Last resort - try absolute imports
        import src.core.input_parser as ip
        import src.core.code_generator as cg
        import src.models.parsed_sentence as ps
        import src.models.translation_result as tr
        
        InputParser = ip.InputParser
        CodeGenerator = cg.CodeGenerator
        ParsedSentence = ps.ParsedSentence
        PatternType = ps.PatternType
        TranslationResult = tr.TranslationResult


@dataclass
class TranslationWarning:
    """Represents a warning about potentially problematic code"""
    warning_type: str
    message: str
    severity: str  # 'low', 'medium', 'high'
    suggestion: Optional[str] = None


class ErrorHandler:
    """Comprehensive error handling for translation engine"""
    
    @staticmethod
    def get_input_examples() -> Dict[str, List[str]]:
        """Get examples of valid input patterns (Requirement 5.5)"""
        return {
            "Arithmetic Operations": [
                "add 5 and 3",
                "multiply x by 2", 
                "divide 10 by 2",
                "subtract 3 from 8"
            ],
            "Variable Assignment": [
                "set x to 10",
                "create variable name with value hello",
                "assign 42 to answer"
            ],
            "Conditional Statements": [
                "if x greater than 5 then print yes",
                "when count equals 0 do print empty",
                "if temperature less than 32 then print freezing else print not freezing"
            ],
            "Data Operations": [
                "create list with 1, 2, 3",
                "add item to my_list",
                "create dictionary with name John and age 25"
            ],
            "Loop Operations": [
                "repeat 5 times print hello",
                "for each item in numbers print item",
                "while x less than 10 increment x"
            ]
        }
    
    @staticmethod
    def generate_informative_error(error_type: str, original_input: str, specific_issue: str = None) -> str:
        """Generate informative error messages (Requirement 5.1)"""
        examples = ErrorHandler.get_input_examples()
        
        if error_type == "empty_input":
            return ("Input cannot be empty. Please enter an English instruction to translate.\n\n"
                   "Examples:\n"
                   "  • add 5 and 3\n"
                   "  • set x to 10\n"
                   "  • create list with 1, 2, 3")
        
        elif error_type == "too_short":
            return ("Input is too short to be meaningful. Please provide a complete instruction.\n\n"
                   "Examples:\n"
                   "  • add 5 and 3\n"
                   "  • multiply x by 2\n"
                   "  • set x to 10\n"
                   "  • if x greater than 5 then print yes")
        
        elif error_type == "unrecognized_pattern":
            message = "Unable to recognize a translatable pattern in your input."
            if specific_issue:
                message += f" Issue: {specific_issue}"
            
            message += "\n\nSupported patterns and examples:"
            for category, pattern_examples in examples.items():
                message += f"\n\n{category}:"
                for example in pattern_examples[:2]:  # Show first 2 examples
                    message += f"\n  • {example}"
            
            return message
        
        elif error_type == "parsing_failed":
            message = f"Failed to parse your input: {specific_issue or 'Unknown parsing error'}"
            message += "\n\nPlease check that your instruction follows one of these patterns:"
            
            # Show relevant examples based on input content
            relevant_examples = ErrorHandler._get_relevant_examples(original_input, examples)
            for category, pattern_examples in relevant_examples.items():
                message += f"\n\n{category}:"
                for example in pattern_examples:
                    message += f"\n  • {example}"
            
            return message
        
        elif error_type == "code_generation_failed":
            return (f"Failed to generate Python code: {specific_issue or 'Unknown generation error'}\n\n"
                   "This might be due to ambiguous or incomplete instructions. "
                   "Try being more specific about what you want to accomplish.")
        
        elif error_type == "unsafe_content":
            return ("Input contains potentially unsafe content that cannot be translated.\n\n"
                   "Please avoid using Python-specific keywords or system commands. "
                   "Focus on basic operations like arithmetic, assignments, and data manipulation.")
        
        else:
            return f"Translation error: {specific_issue or 'Unknown error occurred'}"
    
    @staticmethod
    def _get_relevant_examples(input_text: str, all_examples: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Get examples most relevant to the input text"""
        input_lower = input_text.lower()
        relevant = {}
        
        # Check for arithmetic keywords
        arithmetic_keywords = ['add', 'plus', 'sum', 'multiply', 'times', 'divide', 'subtract', 'minus', 'calculate']
        if any(keyword in input_lower for keyword in arithmetic_keywords):
            relevant["Arithmetic Operations"] = all_examples["Arithmetic Operations"]
        
        # Check for assignment keywords  
        assignment_keywords = ['set', 'create', 'assign', 'variable', 'value']
        if any(keyword in input_lower for keyword in assignment_keywords):
            relevant["Variable Assignment"] = all_examples["Variable Assignment"]
        
        # Check for conditional keywords
        conditional_keywords = ['if', 'when', 'then', 'else', 'condition']
        if any(keyword in input_lower for keyword in conditional_keywords):
            relevant["Conditional Statements"] = all_examples["Conditional Statements"]
        
        # Check for data keywords
        data_keywords = ['list', 'array', 'dictionary', 'dict', 'data']
        if any(keyword in input_lower for keyword in data_keywords):
            relevant["Data Operations"] = all_examples["Data Operations"]
        
        # Check for loop keywords
        loop_keywords = ['repeat', 'loop', 'for', 'while', 'each', 'times']
        if any(keyword in input_lower for keyword in loop_keywords):
            relevant["Loop Operations"] = all_examples["Loop Operations"]
        
        # If no specific keywords found, return all examples
        if not relevant:
            return all_examples
        
        return relevant


class TranslationEngine:
    """
    Main Translation Engine that coordinates parsing and code generation
    """
    
    def __init__(self):
        self.input_parser = InputParser()
        self.code_generator = CodeGenerator()
        self.warnings: List[TranslationWarning] = []
    
    def translate(self, english_sentence: str) -> TranslationResult:
        """
        Main translation method that converts English sentence to Python code
        """
        start_time = time.time()
        self.warnings = []
        
        try:
            # Clean input but preserve original for result
            cleaned_input = english_sentence.strip()
            
            # Validate input
            is_valid, validation_error = self.validate_input(cleaned_input)
            if not is_valid:
                return TranslationResult.create_error(
                    validation_error,
                    english_sentence,
                    time.time() - start_time
                )
            
            # Check if input contains multiple statements
            statements = self._split_multiple_statements(cleaned_input)
            
            if len(statements) > 1:
                # Handle multiple statements
                return self._translate_multiple_statements(statements, english_sentence, start_time)
            
            # Parse the English sentence (single statement)
            try:
                parsed_sentence = self.input_parser.parse_sentence(cleaned_input)
            except Exception as e:
                return self._handle_parsing_error(english_sentence, str(e), start_time)
            
            # Check for ambiguous input and provide suggestions
            ambiguity_warnings = self._check_for_ambiguity(parsed_sentence)
            for warning in ambiguity_warnings:
                self.warnings.append(warning)
            
            # Generate Python code
            try:
                translation_result = self.code_generator.generate(parsed_sentence)
            except Exception as e:
                error_message = ErrorHandler.generate_informative_error("code_generation_failed", english_sentence, str(e))
                return TranslationResult.create_error(
                    error_message,
                    english_sentence,
                    time.time() - start_time
                )
            
            # Check for potentially problematic code
            code_warnings = self._check_for_problematic_code(translation_result.python_code)
            for warning in code_warnings:
                self.warnings.append(warning)
            
            # Add warnings to the result
            for warning in self.warnings:
                translation_result.add_warning(f"[{warning.severity.upper()}] {warning.message}")
                if warning.suggestion:
                    translation_result.add_warning(f"Suggestion: {warning.suggestion}")
            
            # Update timing and preserve original text exactly
            translation_result.translation_time = time.time() - start_time
            translation_result.original_text = english_sentence  # Preserve exact original
            
            return translation_result
            
        except Exception as e:
            return TranslationResult.create_error(
                f"Translation engine error: {str(e)}",
                english_sentence,
                time.time() - start_time
            )
    
    def validate_input(self, sentence: str) -> Tuple[bool, str]:
        """
        Validate input sentence for translation requirements
        """
        # Check for empty input
        if not sentence or not sentence.strip():
            return False, ErrorHandler.generate_informative_error("empty_input", sentence)
        
        # Use the input parser's validation
        is_valid, error_message = self.input_parser.validate_input(sentence)
        
        if not is_valid:
            # Determine error type based on the error message
            if "empty" in error_message.lower():
                return False, ErrorHandler.generate_informative_error("empty_input", sentence)
            elif "too short" in error_message.lower():
                return False, ErrorHandler.generate_informative_error("too_short", sentence)
            elif "unsafe" in error_message.lower():
                return False, ErrorHandler.generate_informative_error("unsafe_content", sentence, error_message)
            else:
                return False, ErrorHandler.generate_informative_error("parsing_failed", sentence, error_message)
        
        # Additional validation specific to translation
        sentence_lower = sentence.lower().strip()
        
        # Check for minimum meaningful content
        if len(sentence_lower.split()) < 2:
            return False, ErrorHandler.generate_informative_error("too_short", sentence)
        
        # Check for supported patterns
        pattern_type = self.input_parser.identify_pattern(sentence)
        if pattern_type == PatternType.UNKNOWN:
            return False, ErrorHandler.generate_informative_error("unrecognized_pattern", sentence)
        
        return True, "Input is valid for translation"
    

    
    def _handle_parsing_error(self, sentence: str, error: str, start_time: float) -> TranslationResult:
        """Handle parsing errors with helpful suggestions"""
        error_message = ErrorHandler.generate_informative_error("parsing_failed", sentence, error)
        
        return TranslationResult.create_error(
            error_message,
            sentence,
            time.time() - start_time
        )
    
    def _check_for_ambiguity(self, parsed_sentence: ParsedSentence) -> List[TranslationWarning]:
        """Check for ambiguous input and generate suggestions"""
        warnings = []
        
        # Check confidence level
        confidence = parsed_sentence.metadata.get('confidence', 0.0)
        if confidence < 0.7:
            warnings.append(TranslationWarning(
                warning_type="ambiguity",
                message="Input may be ambiguous or unclear",
                severity="medium",
                suggestion="Try being more specific about the operation you want to perform"
            ))
        
        # Check for missing variable values
        unvalued_vars = [name for name, value in parsed_sentence.variables.items() if value is None]
        if unvalued_vars:
            warnings.append(TranslationWarning(
                warning_type="ambiguity",
                message=f"Variables without clear values: {', '.join(unvalued_vars)}",
                severity="low",
                suggestion="Consider specifying values for these variables"
            ))
        
        # Check for operations without clear operands
        for operation in parsed_sentence.operations:
            if len(operation.operands) < 2 and operation.operation_type in ['add', 'subtract', 'multiply', 'divide']:
                warnings.append(TranslationWarning(
                    warning_type="ambiguity",
                    message=f"Arithmetic operation '{operation.operation_type}' may be missing operands",
                    severity="medium",
                    suggestion="Ensure both operands are clearly specified"
                ))
        
        return warnings
    
    def _check_for_problematic_code(self, python_code: str) -> List[TranslationWarning]:
        """Check generated code for potential runtime issues"""
        warnings = []
        
        if not python_code.strip():
            return warnings
        
        code_lower = python_code.lower()
        
        # Check for division operations (potential division by zero)
        if '/' in python_code and '//' not in python_code:
            warnings.append(TranslationWarning(
                warning_type="runtime_risk",
                message="Code contains division operation - watch out for division by zero",
                severity="medium",
                suggestion="Ensure divisor is not zero before executing"
            ))
        
        # Check for undefined variables (basic check)
        lines = python_code.split('\n')
        defined_vars = set()
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                # Extract variable being assigned
                var_part = line.split('=')[0].strip()
                if var_part.isidentifier():
                    defined_vars.add(var_part)
        
        # Look for variables used but not defined
        import re
        used_vars = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', python_code))
        python_builtins = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'append'}
        undefined_vars = used_vars - defined_vars - python_builtins
        
        if undefined_vars:
            warnings.append(TranslationWarning(
                warning_type="runtime_risk",
                message=f"Potentially undefined variables: {', '.join(sorted(undefined_vars))}",
                severity="high",
                suggestion="Make sure these variables are defined before use"
            ))
        
        # Check for infinite loops (basic patterns)
        if 'while True:' in python_code or 'while 1:' in python_code:
            warnings.append(TranslationWarning(
                warning_type="runtime_risk",
                message="Code contains potential infinite loop",
                severity="high",
                suggestion="Ensure loop has proper exit condition"
            ))
        
        # Check for large range operations
        range_matches = re.findall(r'range\((\d+)\)', python_code)
        for match in range_matches:
            if int(match) > 10000:
                warnings.append(TranslationWarning(
                    warning_type="performance",
                    message=f"Large range operation detected: range({match})",
                    severity="medium",
                    suggestion="Consider if this large range is intentional"
                ))
        
        return warnings
    
    def get_supported_patterns(self) -> Dict[str, List[str]]:
        """Get list of supported English patterns with examples"""
        return {
            "Arithmetic Operations": [
                "add 5 and 3",
                "multiply x by 2",
                "calculate 10 plus 7",
                "divide total by count"
            ],
            "Variable Assignment": [
                "set x to 10",
                "create variable name with value hello",
                "assign 42 to answer"
            ],
            "Conditional Statements": [
                "if x greater than 5 then print yes",
                "when count equals 0 do print empty",
                "if temperature less than 32 then print freezing else print not freezing"
            ],
            "Data Operations": [
                "create list with 1, 2, 3",
                "add item to my_list",
                "create dictionary with name John and age 25"
            ],
            "Loop Operations": [
                "repeat 5 times print hello",
                "for each item in numbers print item",
                "while x less than 10 increment x"
            ]
        }
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get statistics about the translation engine"""
        return {
            "supported_patterns": len(self.get_supported_patterns()),
            "parser_confidence_threshold": 0.7,
            "warning_categories": ["ambiguity", "runtime_risk", "performance"],
            "validation_checks": [
                "input_length",
                "pattern_recognition", 
                "syntax_validation",
                "variable_analysis"
            ]
        }
    
    def _split_multiple_statements(self, input_text: str) -> List[str]:
        """Split input text into individual statements"""
        import re
        
        # First, split by newlines
        lines = input_text.strip().split('\n')
        statements = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                statements.append(line)
        
        # If we have multiple lines, return them
        if len(statements) > 1:
            return statements
        
        # If single line, try to detect multiple statements
        if len(statements) == 1:
            single_line = statements[0]
            
            # Look for patterns that indicate statement boundaries
            # More specific patterns to avoid false positives
            statement_patterns = [
                r'(?<=\w)\s*(?=set\s+\w+\s+to\s+)',           # After word, before "set var to"
                r'(?<=\w)\s*(?=if\s+\w+\s+\w+\s+than\s+)',    # After word, before "if var op than"
                r'(?<=\w)\s*(?=when\s+\w+\s+\w+\s+)',         # After word, before "when var op"
                r'(?<=\w)\s*(?=create\s+)',                   # After word, before "create"
                r'(?<=\w)\s*(?=add\s+\w+\s+and\s+)',          # After word, before "add X and Y"
                r'(?<=\w)\s*(?=multiply\s+\w+\s+by\s+)',      # After word, before "multiply X by Y"
                r'(?<=\w)\s*(?=subtract\s+\w+\s+from\s+)',    # After word, before "subtract X from Y"
                r'(?<=\w)\s*(?=divide\s+\w+\s+by\s+)',        # After word, before "divide X by Y"
            ]
            
            # Try each pattern to split
            for pattern in statement_patterns:
                parts = re.split(pattern, single_line)
                if len(parts) > 1:
                    # Clean up parts
                    cleaned_parts = [part.strip() for part in parts if part.strip()]
                    if len(cleaned_parts) > 1:
                        return cleaned_parts
            
            # If no pattern worked, try a more aggressive approach
            # Look for common statement beginnings without word boundaries
            aggressive_patterns = [
                r'(set\s+\w+\s+to\s+[^s]*?)(?=set\s+)',
                r'(if\s+[^i]*?)(?=if\s+)',
                r'(when\s+[^w]*?)(?=when\s+)',
                r'(set\s+[^s]*?)(?=if\s+)',
                r'(set\s+[^s]*?)(?=when\s+)',
            ]
            
            for pattern in aggressive_patterns:
                matches = re.findall(pattern, single_line)
                if matches:
                    # Find what's left after all matches
                    remaining = single_line
                    for match in matches:
                        remaining = remaining.replace(match, '', 1)
                    
                    result = matches + [remaining.strip()] if remaining.strip() else matches
                    if len(result) > 1:
                        return result
        
        # Return original as single statement
        return [input_text.strip()]
    
    def _translate_multiple_statements(self, statements: List[str], original_input: str, start_time: float) -> TranslationResult:
        """Translate multiple statements and combine the results"""
        all_code = []
        all_warnings = []
        
        for i, statement in enumerate(statements):
            # Translate each statement individually
            result = self.translate(statement)
            
            if result.success:
                all_code.append(result.python_code)
                all_warnings.extend(result.warnings)
            else:
                # If any statement fails, return error with context
                error_msg = f"Error in statement {i+1} ('{statement}'): {result.error_message}"
                return TranslationResult.create_error(
                    error_msg,
                    original_input,
                    time.time() - start_time
                )
        
        # Combine all code
        combined_code = '\n'.join(all_code)
        
        # Create successful result
        result = TranslationResult.create_success(
            combined_code,
            original_input,
            time.time() - start_time
        )
        
        # Add all warnings
        for warning in all_warnings:
            result.add_warning(warning)
        
        # Add info about multiple statements
        result.add_warning(f"[INFO] Processed {len(statements)} statements")
        
        return result