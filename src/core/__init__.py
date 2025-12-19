"""
Core components package for English to Python Translator

This package contains the core processing components:
- InputParser: Analyzes and parses English sentences
- CodeGenerator: Generates Python code from parsed structures (to be implemented)
"""

from .input_parser import InputParser, PatternMatcher, Token, TokenType

__all__ = [
    'InputParser',
    'PatternMatcher', 
    'Token',
    'TokenType'
]