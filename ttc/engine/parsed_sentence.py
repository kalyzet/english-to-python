"""
ParsedSentence data model for English to Python Translator
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class PatternType(Enum):
    """Enum for different pattern types that can be identified in English sentences"""
    ARITHMETIC = "arithmetic"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    DATA_OPERATION = "data_operation"
    ASSIGNMENT = "assignment"
    UNKNOWN = "unknown"


@dataclass
class Condition:
    """Represents a conditional statement in parsed sentence"""
    condition_text: str
    condition_type: str  # 'if', 'while', 'when', etc.
    variables_used: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate condition after initialization"""
        if not self.condition_text.strip():
            raise ValueError("Condition text cannot be empty")


@dataclass
class Operation:
    """Represents an operation in parsed sentence"""
    operation_type: str  # 'add', 'subtract', 'multiply', 'divide', 'assign'
    operands: List[str] = field(default_factory=list)
    result_variable: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate operation after initialization"""
        if not self.operation_type.strip():
            raise ValueError("Operation type cannot be empty")
        
        # Validate operation types
        valid_operations = {
            'add', 'subtract', 'multiply', 'divide', 'assign',
            'create', 'append', 'remove', 'update', 'get'
        }
        if self.operation_type not in valid_operations:
            raise ValueError(f"Invalid operation type: {self.operation_type}")
    
    def is_arithmetic(self) -> bool:
        """Check if this is an arithmetic operation"""
        return self.operation_type in {'add', 'subtract', 'multiply', 'divide'}
    
    def is_assignment(self) -> bool:
        """Check if this is an assignment operation"""
        return self.operation_type == 'assign'
    
    def is_data_operation(self) -> bool:
        """Check if this is a data structure operation"""
        return self.operation_type in {'create', 'append', 'remove', 'update', 'get'}


@dataclass
class ParsedSentence:
    """
    Represents a parsed English sentence with extracted information
    for code generation
    """
    original_text: str
    pattern_type: PatternType = PatternType.UNKNOWN
    variables: Dict[str, Any] = field(default_factory=dict)
    operations: List[Operation] = field(default_factory=list)
    conditions: List[Condition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate parsed sentence after initialization"""
        if not self.original_text.strip():
            raise ValueError("Original text cannot be empty")
    
    def add_variable(self, name: str, value: Any) -> None:
        """Add a variable to the parsed sentence"""
        if not name.strip():
            raise ValueError("Variable name cannot be empty")
        self.variables[name] = value
    
    def add_operation(self, operation: Operation) -> None:
        """Add an operation to the parsed sentence"""
        if not isinstance(operation, Operation):
            raise TypeError("Expected Operation instance")
        self.operations.append(operation)
    
    def add_condition(self, condition: Condition) -> None:
        """Add a condition to the parsed sentence"""
        if not isinstance(condition, Condition):
            raise TypeError("Expected Condition instance")
        self.conditions.append(condition)
    
    def get_variable_names(self) -> List[str]:
        """Get list of all variable names in the sentence"""
        return list(self.variables.keys())
    
    def has_arithmetic_operations(self) -> bool:
        """Check if sentence contains arithmetic operations"""
        return any(op.is_arithmetic() for op in self.operations)
    
    def has_conditions(self) -> bool:
        """Check if sentence contains conditional statements"""
        return len(self.conditions) > 0
    
    def is_valid(self) -> bool:
        """Check if the parsed sentence is valid for code generation"""
        return (
            self.pattern_type != PatternType.UNKNOWN and
            (len(self.operations) > 0 or len(self.conditions) > 0 or len(self.variables) > 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parsed sentence to dictionary representation"""
        return {
            'original_text': self.original_text,
            'pattern_type': self.pattern_type.value,
            'variables': self.variables,
            'operations': [
                {
                    'operation_type': op.operation_type,
                    'operands': op.operands,
                    'result_variable': op.result_variable
                }
                for op in self.operations
            ],
            'conditions': [
                {
                    'condition_text': cond.condition_text,
                    'condition_type': cond.condition_type,
                    'variables_used': cond.variables_used
                }
                for cond in self.conditions
            ],
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedSentence':
        """Create ParsedSentence from dictionary representation"""
        sentence = cls(
            original_text=data['original_text'],
            pattern_type=PatternType(data['pattern_type']),
            variables=data.get('variables', {}),
            metadata=data.get('metadata', {})
        )
        
        # Add operations
        for op_data in data.get('operations', []):
            operation = Operation(
                operation_type=op_data['operation_type'],
                operands=op_data['operands'],
                result_variable=op_data.get('result_variable')
            )
            sentence.add_operation(operation)
        
        # Add conditions
        for cond_data in data.get('conditions', []):
            condition = Condition(
                condition_text=cond_data['condition_text'],
                condition_type=cond_data['condition_type'],
                variables_used=cond_data.get('variables_used', [])
            )
            sentence.add_condition(condition)
        
        return sentence