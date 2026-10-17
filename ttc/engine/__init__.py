"""
Engine package: parsing, code generation, and translation orchestration.
"""

from .parsed_sentence import ParsedSentence, Operation, Condition, PatternType
from .translation_result import TranslationResult, ExecutionResult
from .parser import InputParser, PatternMatcher, Token, TokenType
from .generator import CodeGenerator
from .translator import TranslationEngine, TranslationWarning

__all__ = [
    "ParsedSentence",
    "Operation",
    "Condition",
    "PatternType",
    "TranslationResult",
    "ExecutionResult",
    "InputParser",
    "PatternMatcher",
    "Token",
    "TokenType",
    "CodeGenerator",
    "TranslationEngine",
    "TranslationWarning",
]
