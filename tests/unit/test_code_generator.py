"""
Unit tests for Code Generator component
"""

import pytest
import ast
from src.core.code_generator import CodeGenerator
from src.models.parsed_sentence import ParsedSentence, Operation, Condition, PatternType
from src.models.translation_result import TranslationResult