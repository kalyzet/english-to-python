"""
Data models package for English to Python Translator

This package contains all the data models used throughout the application:
- ParsedSentence: Represents parsed English sentences with extracted information
- Operation: Represents operations within parsed sentences
- Condition: Represents conditional statements
- TranslationResult: Represents the result of translation process
- ExecutionResult: Represents the result of code execution
"""

from .parsed_sentence import (
    ParsedSentence,
    Operation,
    Condition,
    PatternType
)
from .translation_result import (
    TranslationResult,
    ExecutionResult
)

__all__ = [
    'ParsedSentence',
    'Operation', 
    'Condition',
    'PatternType',
    'TranslationResult',
    'ExecutionResult'
]