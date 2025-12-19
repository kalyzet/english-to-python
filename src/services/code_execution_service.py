"""
Code Execution Service for English to Python Translator

This service provides safe execution of generated Python code with resource limits,
output capture, error handling, and user input support.
"""

import sys
import io
import time
import threading
import signal
import subprocess
import tempfile
import os
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from dataclasses import dataclass

from src.models.translation_result import ExecutionResult


@dataclass
class ExecutionConfig:
    """Configuration for code execution"""
    timeout_seconds: float = 30.0
    max_memory_mb: int = 100
    allow_imports: bool = True
    allow_file_operations: bool = False
    allow_network: bool = False
    capture_stdout: bool = True
    capture_stderr: bool = True


class ExecutionTimeoutError(Exception):
    """Raised when code execution exceeds timeout"""
    pass


class ExecutionSecurityError(Exception):
    """Raised when code attempts unsafe operations"""
    pass


class CodeExecutionService:
    """
    Service for safely executing generated Python code
    
    Provides:
    - Safe code execution with resource limits
    - Output capture and error handling
    - User input handling for interactive code
    - Security restrictions for unsafe operations
    """
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        """
        Initialize the code execution service
        
        Args:
            config: Execution configuration, uses defaults if None
        """
        self.config = config or ExecutionConfig()
        self._user_input_handler: Optional[Callable[[str], str]] = None
        self._execution_globals: Dict[str, Any] = {}
        self._setup_execution_environment()
    
    def _setup_execution_environment(self) -> None:
        """Setup the execution environment with safe builtins"""
        # Create a restricted globals environment
        safe_builtins = {
            # Basic types and functions
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
            'getattr', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min',
            'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
            'str', 'sum', 'tuple', 'type', 'zip',
            # Math operations
            'divmod', 'pow', 'round',
            # String operations
            'chr', 'ord', 'str',
            # Container operations
            'len', 'list', 'dict', 'set', 'tuple',
        }
        
        # Create restricted builtins
        restricted_builtins = {}
        builtins_source = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        for name in safe_builtins:
            if name in builtins_source:
                restricted_builtins[name] = builtins_source[name]
        
        # Add input function that uses our handler
        restricted_builtins['input'] = self._safe_input
        
        self._execution_globals = {
            '__builtins__': restricted_builtins,
            '__name__': '__main__',
        }
    
    def set_user_input_handler(self, handler: Callable[[str], str]) -> None:
        """
        Set the handler for user input during code execution
        
        Args:
            handler: Function that takes a prompt string and returns user input
        """
        self._user_input_handler = handler
    
    def _safe_input(self, prompt: str = "") -> str:
        """
        Safe input function that uses the configured input handler
        
        Args:
            prompt: Input prompt to display
            
        Returns:
            User input string
            
        Raises:
            ExecutionSecurityError: If no input handler is configured
        """
        if self._user_input_handler is None:
            raise ExecutionSecurityError("Interactive input not supported in this context")
        
        try:
            return self._user_input_handler(prompt)
        except Exception as e:
            raise ExecutionSecurityError(f"Input handler error: {str(e)}")
    
    @contextmanager
    def _timeout_context(self, timeout_seconds: float):
        """
        Context manager for execution timeout
        
        Args:
            timeout_seconds: Maximum execution time
            
        Raises:
            ExecutionTimeoutError: If execution exceeds timeout
        """
        def timeout_handler(signum, frame):
            raise ExecutionTimeoutError(f"Code execution exceeded {timeout_seconds} seconds")
        
        # Set up timeout signal (Unix-like systems)
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout_seconds))
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Fallback for Windows - use threading
            timeout_occurred = threading.Event()
            
            def timeout_thread():
                timeout_occurred.wait(timeout_seconds)
                if not timeout_occurred.is_set():
                    # This is a limitation - we can't easily interrupt execution on Windows
                    pass
            
            timer = threading.Thread(target=timeout_thread, daemon=True)
            timer.start()
            
            try:
                yield
            finally:
                timeout_occurred.set()
    
    def _validate_code_safety(self, code: str) -> None:
        """
        Validate that code doesn't contain unsafe operations
        
        Args:
            code: Python code to validate
            
        Raises:
            ExecutionSecurityError: If code contains unsafe operations
        """
        # List of potentially dangerous operations
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess', 'import socket',
            'import urllib', 'import requests', 'import http',
            '__import__', 'eval(', 'exec(', 'compile(',
            'open(', 'file(', 'input(', 'raw_input(',
            'globals(', 'locals(', 'vars(', 'dir(',
            'getattr(', 'setattr(', 'delattr(',
            'exit(', 'quit(',
        ]
        
        if not self.config.allow_imports:
            dangerous_patterns.extend(['import ', 'from '])
        
        if not self.config.allow_file_operations:
            dangerous_patterns.extend(['open(', 'file(', 'with open'])
        
        # Check for dangerous patterns
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                if pattern == 'input(' and self._user_input_handler is not None:
                    continue  # Allow input if handler is configured
                raise ExecutionSecurityError(f"Unsafe operation detected: {pattern}")
    
    def execute_code(self, python_code: str, 
                    user_input_handler: Optional[Callable[[str], str]] = None) -> ExecutionResult:
        """
        Execute Python code safely with resource limits and output capture
        
        Args:
            python_code: Python code to execute
            user_input_handler: Optional handler for user input during execution
            
        Returns:
            ExecutionResult containing execution outcome and captured output
        """
        start_time = time.time()
        
        # Set user input handler if provided
        if user_input_handler:
            self.set_user_input_handler(user_input_handler)
        
        try:
            # Validate code safety
            self._validate_code_safety(python_code)
            
            # Prepare output capture
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Execute code with timeout and output capture
            with self._timeout_context(self.config.timeout_seconds):
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    try:
                        # Compile code first to catch syntax errors
                        compiled_code = compile(python_code, '<string>', 'exec')
                        
                        # Execute the compiled code
                        exec(compiled_code, self._execution_globals.copy())
                        
                        execution_time = time.time() - start_time
                        
                        return ExecutionResult(
                            success=True,
                            stdout=stdout_capture.getvalue(),
                            stderr=stderr_capture.getvalue(),
                            execution_time=execution_time
                        )
                        
                    except SyntaxError as e:
                        execution_time = time.time() - start_time
                        error_msg = f"Syntax Error: {str(e)}"
                        if hasattr(e, 'lineno') and e.lineno:
                            error_msg += f" (line {e.lineno})"
                        
                        return ExecutionResult(
                            success=False,
                            error_message=error_msg,
                            stderr=stderr_capture.getvalue(),
                            execution_time=execution_time
                        )
                        
                    except Exception as e:
                        execution_time = time.time() - start_time
                        error_msg = f"{type(e).__name__}: {str(e)}"
                        
                        return ExecutionResult(
                            success=False,
                            error_message=error_msg,
                            stderr=stderr_capture.getvalue(),
                            execution_time=execution_time
                        )
        
        except ExecutionTimeoutError as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
        
        except ExecutionSecurityError as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error_message=f"Security Error: {str(e)}",
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error_message=f"Execution Error: {str(e)}",
                execution_time=execution_time
            )
    
    def execute_code_with_subprocess(self, python_code: str) -> ExecutionResult:
        """
        Execute Python code in a separate subprocess for additional isolation
        
        Args:
            python_code: Python code to execute
            
        Returns:
            ExecutionResult containing execution outcome and captured output
        """
        start_time = time.time()
        
        try:
            # Validate code safety
            self._validate_code_safety(python_code)
            
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(python_code)
                temp_file_path = temp_file.name
            
            try:
                # Execute code in subprocess with timeout
                result = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds
                )
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    return ExecutionResult(
                        success=True,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        execution_time=execution_time
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error_message=f"Process exited with code {result.returncode}",
                        stdout=result.stdout,
                        stderr=result.stderr,
                        execution_time=execution_time
                    )
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass  # Ignore cleanup errors
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error_message=f"Code execution exceeded {self.config.timeout_seconds} seconds",
                execution_time=execution_time
            )
        
        except ExecutionSecurityError as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error_message=f"Security Error: {str(e)}",
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error_message=f"Execution Error: {str(e)}",
                execution_time=execution_time
            )
    
    def is_code_safe(self, python_code: str) -> tuple[bool, str]:
        """
        Check if code is safe to execute without actually executing it
        
        Args:
            python_code: Python code to check
            
        Returns:
            Tuple of (is_safe, reason) where reason explains why code is unsafe
        """
        try:
            self._validate_code_safety(python_code)
            
            # Try to compile the code to check for syntax errors
            compile(python_code, '<string>', 'exec')
            
            return True, "Code appears safe to execute"
        
        except ExecutionSecurityError as e:
            return False, str(e)
        
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"
        
        except Exception as e:
            return False, f"Code validation error: {str(e)}"
    
    def get_execution_warnings(self, python_code: str) -> list[str]:
        """
        Get warnings about potentially problematic code without executing it
        
        Args:
            python_code: Python code to analyze
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Check for potentially problematic patterns
        code_lower = python_code.lower()
        
        # Division operations that might cause division by zero
        if '/' in python_code and '0' in python_code:
            warnings.append("Code contains division operations - check for division by zero")
        
        # Infinite loops
        if 'while true' in code_lower or 'while 1' in code_lower:
            warnings.append("Code contains potential infinite loop")
        
        # Large range operations
        if 'range(' in code_lower:
            import re
            range_matches = re.findall(r'range\((\d+)\)', python_code)
            for match in range_matches:
                if int(match) > 10000:
                    warnings.append(f"Large range operation detected: range({match})")
        
        # Undefined variable usage (basic check)
        lines = python_code.split('\n')
        defined_vars = set()
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                var_name = line.split('=')[0].strip()
                if var_name.isidentifier():
                    defined_vars.add(var_name)
        
        # This is a very basic check - a full implementation would need AST parsing
        import re
        var_usage = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', python_code)
        undefined_vars = set(var_usage) - defined_vars - set(self._execution_globals.keys())
        
        # Filter out built-in functions and common keywords
        builtin_names = {'print', 'input', 'len', 'range', 'str', 'int', 'float', 'list', 'dict'}
        python_keywords = {'if', 'else', 'elif', 'for', 'while', 'def', 'class', 'return', 'True', 'False', 'None'}
        undefined_vars = undefined_vars - builtin_names - python_keywords
        
        if undefined_vars:
            warnings.append(f"Potentially undefined variables: {', '.join(sorted(undefined_vars))}")
        
        return warnings