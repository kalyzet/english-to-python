"""
TranslationResult data model for English to Python Translator
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionResult:
    """
    Represents the result of executing generated Python code
    """
    success: bool
    output: str = ""
    error_message: str = ""
    execution_time: float = 0.0
    return_value: Any = None
    stdout: str = ""
    stderr: str = ""
    
    def __post_init__(self) -> None:
        """Validate execution result after initialization"""
        if self.execution_time < 0:
            raise ValueError("Execution time cannot be negative")
    
    def has_output(self) -> bool:
        """Check if execution produced any output"""
        return bool(self.output.strip() or self.stdout.strip())
    
    def has_error(self) -> bool:
        """Check if execution resulted in an error"""
        return not self.success or bool(self.error_message.strip() or self.stderr.strip())
    
    def get_combined_output(self) -> str:
        """Get combined output from all sources"""
        outputs = []
        if self.output.strip():
            outputs.append(self.output.strip())
        if self.stdout.strip():
            outputs.append(self.stdout.strip())
        return "\n".join(outputs)
    
    def get_combined_error(self) -> str:
        """Get combined error messages from all sources"""
        errors = []
        if self.error_message.strip():
            errors.append(self.error_message.strip())
        if self.stderr.strip():
            errors.append(self.stderr.strip())
        return "\n".join(errors)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution result to dictionary representation"""
        return {
            'success': self.success,
            'output': self.output,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'return_value': self.return_value,
            'stdout': self.stdout,
            'stderr': self.stderr
        }


@dataclass
class TranslationResult:
    """
    Represents the result of translating English text to Python code
    """
    success: bool
    python_code: str = ""
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    execution_result: Optional[ExecutionResult] = None
    original_text: str = ""
    translation_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate translation result after initialization"""
        if self.translation_time < 0:
            raise ValueError("Translation time cannot be negative")
        
        if self.success and not self.python_code.strip():
            raise ValueError("Successful translation must have non-empty Python code")
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the result"""
        if warning.strip():
            self.warnings.append(warning.strip())
    
    def has_warnings(self) -> bool:
        """Check if translation has any warnings"""
        return len(self.warnings) > 0
    
    def has_execution_result(self) -> bool:
        """Check if translation result includes execution result"""
        return self.execution_result is not None
    
    def is_executable(self) -> bool:
        """Check if the generated code is potentially executable"""
        return (
            self.success and 
            self.python_code.strip() and 
            not self.has_critical_errors()
        )
    
    def has_critical_errors(self) -> bool:
        """Check if there are critical errors that prevent execution"""
        critical_keywords = ['SyntaxError', 'IndentationError', 'NameError']
        return any(keyword in self.error_message for keyword in critical_keywords)
    
    def get_formatted_code(self) -> str:
        """Get formatted Python code with proper indentation"""
        if not self.python_code:
            return ""
        
        lines = self.python_code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Basic formatting - remove extra whitespace
            formatted_line = line.strip()
            if formatted_line:
                formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    def get_summary(self) -> str:
        """Get a summary of the translation result"""
        if self.success:
            summary = f"✓ Translation successful"
            if self.has_warnings():
                summary += f" (with {len(self.warnings)} warnings)"
            if self.has_execution_result():
                if self.execution_result.success:
                    summary += " - Code executed successfully"
                else:
                    summary += " - Code execution failed"
        else:
            summary = f"✗ Translation failed: {self.error_message}"
        
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert translation result to dictionary representation"""
        result_dict = {
            'success': self.success,
            'python_code': self.python_code,
            'error_message': self.error_message,
            'warnings': self.warnings,
            'original_text': self.original_text,
            'translation_time': self.translation_time,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
        
        if self.execution_result:
            result_dict['execution_result'] = self.execution_result.to_dict()
        
        return result_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationResult':
        """Create TranslationResult from dictionary representation"""
        execution_result = None
        if 'execution_result' in data:
            exec_data = data['execution_result']
            execution_result = ExecutionResult(
                success=exec_data['success'],
                output=exec_data.get('output', ''),
                error_message=exec_data.get('error_message', ''),
                execution_time=exec_data.get('execution_time', 0.0),
                return_value=exec_data.get('return_value'),
                stdout=exec_data.get('stdout', ''),
                stderr=exec_data.get('stderr', '')
            )
        
        timestamp = datetime.now()
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'])
            except (ValueError, TypeError):
                pass  # Use default timestamp if parsing fails
        
        return cls(
            success=data['success'],
            python_code=data.get('python_code', ''),
            error_message=data.get('error_message', ''),
            warnings=data.get('warnings', []),
            execution_result=execution_result,
            original_text=data.get('original_text', ''),
            translation_time=data.get('translation_time', 0.0),
            timestamp=timestamp,
            metadata=data.get('metadata', {})
        )
    
    @classmethod
    def create_success(cls, python_code: str, original_text: str = "", 
                      translation_time: float = 0.0) -> 'TranslationResult':
        """Create a successful translation result"""
        return cls(
            success=True,
            python_code=python_code,
            original_text=original_text,
            translation_time=translation_time
        )
    
    @classmethod
    def create_error(cls, error_message: str, original_text: str = "",
                    translation_time: float = 0.0) -> 'TranslationResult':
        """Create a failed translation result"""
        return cls(
            success=False,
            error_message=error_message,
            original_text=original_text,
            translation_time=translation_time
        )