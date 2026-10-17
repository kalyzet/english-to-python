"""
text-to-code (ttc): English to Python translator engine.

Public API:
    from ttc import TranslationEngine
    engine = TranslationEngine()
    result = engine.translate("set age to 25")
"""

__version__ = "0.2.0"

from .engine.translator import TranslationEngine, TranslationWarning
from .engine.parser import InputParser, PatternMatcher, Token, TokenType
from .engine.generator import CodeGenerator
from .engine.parsed_sentence import ParsedSentence, Operation, Condition, PatternType
from .engine.translation_result import TranslationResult, ExecutionResult
from .sandbox import CodeExecutionService, ExecutionConfig, ExecutionTimeoutError, ExecutionSecurityError

__all__ = [
    "__version__",
    "TranslationEngine",
    "TranslationWarning",
    "InputParser",
    "PatternMatcher",
    "Token",
    "TokenType",
    "CodeGenerator",
    "ParsedSentence",
    "Operation",
    "Condition",
    "PatternType",
    "TranslationResult",
    "ExecutionResult",
    "CodeExecutionService",
    "ExecutionConfig",
    "ExecutionTimeoutError",
    "ExecutionSecurityError",
]
