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
            
            # Parse the English sentence
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
                return TranslationResult.create_error(
                    f"Code generation failed: {str(e)}",
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
        # Use the input parser's validation
        is_valid, error_message = self.input_parser.validate_input(sentence)
        
        if not is_valid:
            return False, error_message
        
        # Additional validation specific to translation
        sentence_lower = sentence.lower().strip()
        
        # Check for minimum meaningful content
        if len(sentence_lower.split()) < 2:
            return False, "Input must contain at least 2 words to be translatable"
        
        # Check for supported patterns
        pattern_type = self.input_parser.identify_pattern(sentence)
        if pattern_type == PatternType.UNKNOWN:
            return False, self._generate_pattern_suggestion(sentence)
        
        return True, "Input is valid for translation"
    
    def _generate_pattern_suggestion(self, sentence: str) -> str:
        """Generate helpful suggestions for unrecognized patterns"""
        base_message = "Unable to recognize a translatable pattern in the input."
        
        examples = [
            "Arithmetic: 'add 5 and 3', 'multiply x by 2'",
            "Assignment: 'set x to 10', 'create variable name with value hello'",
            "Conditional: 'if x greater than 5 then print yes'",
            "Data operations: 'create list with 1, 2, 3', 'add item to my_list'"
        ]
        
        return f"{base_message} Try one of these patterns:\n" + "\n".join(f"- {ex}" for ex in examples)
    
    def _handle_parsing_error(self, sentence: str, error: str, start_time: float) -> TranslationResult:
        """Handle parsing errors with helpful suggestions"""
        error_message = f"Failed to parse input: {error}"
        
        # Provide specific suggestions based on common parsing issues
        if "empty" in error.lower():
            error_message += "\nSuggestion: Please provide a non-empty English instruction."
        elif "unsafe" in error.lower():
            error_message += "\nSuggestion: Please avoid using Python-specific keywords or potentially dangerous content."
        else:
            error_message += f"\n{self._generate_pattern_suggestion(sentence)}"
        
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