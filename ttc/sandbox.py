"""
Code Execution Service for English to Python Translator.

Executes generated Python code in an isolated subprocess:

- structural (AST-based) safety validation before anything is spawned,
- restricted builtins inside the child process,
- real timeout enforcement by killing the process tree (works on Windows),
- output/error capture and interactive input() support via a line protocol.
"""

import ast
import json
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Optional, TextIO, Tuple, cast

from .engine.translation_result import ExecutionResult
from .runner import INPUT_SENTINEL

# Package root (parent of the ttc package) so the child can resolve `python -m ttc.runner`
_PACKAGE_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_CAPTURE_CHARS = 1_000_000
_TRUNCATION_MARKER = "\n...[output truncated]..."


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


def analyze_code(python_code: str, config: ExecutionConfig) -> Optional[str]:
    """
    Statically analyze code before execution.

    Returns an error message when the code must not run, else None.
    """
    try:
        tree = ast.parse(python_code)
    except SyntaxError as exc:
        line = f"Line {exc.lineno}: " if exc.lineno else ""
        return f"SyntaxError: {line}{exc.msg}"
    except ValueError as exc:
        return f"SyntaxError: {exc}"

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and not config.allow_imports:
            return "SecurityError: import statements are not allowed"
        if isinstance(node, ast.Attribute):
            name = node.attr
            if name.startswith("__") and name.endswith("__"):
                return f"SecurityError: access to '{name}' is not allowed"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ("eval", "exec", "compile"):
                return f"SecurityError: call to '{func_name}' is not allowed"
            if func_name == "open" and not config.allow_file_operations:
                return "SecurityError: file operations are not allowed"

    return None


class CodeExecutionService:
    """
    Service for safely executing generated Python code.

    Provides:
    - Isolated subprocess execution with real timeout enforcement
    - Output capture and error reporting
    - Interactive input() support through a user input handler
    - Structural safety validation (imports / dunder / eval / open)
    """

    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()

    def execute_code(
        self,
        python_code: str,
        user_input_handler: Optional[Callable[[str], str]] = None,
    ) -> ExecutionResult:
        """
        Execute Python code in an isolated subprocess.

        Args:
            python_code: Python code to execute.
            user_input_handler: Optional callback invoked for each input() prompt;
                its return value is fed back to the running code.

        Returns:
            ExecutionResult containing execution outcome and captured output.
        """
        start_time = time.time()

        safety_error = analyze_code(python_code, self.config)
        if safety_error is not None:
            return ExecutionResult(
                success=False,
                error_message=safety_error,
                execution_time=time.time() - start_time,
            )

        try:
            return self._run_subprocess(python_code, user_input_handler, start_time)
        except Exception as exc:
            return ExecutionResult(
                success=False,
                error_message=f"Execution Error: {exc}",
                execution_time=time.time() - start_time,
            )

    def _run_subprocess(
        self,
        python_code: str,
        user_input_handler: Optional[Callable[[str], str]],
        start_time: float,
    ) -> ExecutionResult:
        payload = json.dumps({
            "code": python_code,
            "allow_imports": self.config.allow_imports,
            "interactive": user_input_handler is not None,
        })

        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            _PACKAGE_PARENT + os.pathsep + existing if existing else _PACKAGE_PARENT
        )

        process = subprocess.Popen(
            [sys.executable, "-u", "-m", "ttc.runner"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
        )
        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None
        stdin_pipe = cast(TextIO, process.stdin)
        stdout_pipe = cast(TextIO, process.stdout)
        stderr_pipe = cast(TextIO, process.stderr)

        stdout_parts: List[str] = []
        stderr_parts: List[str] = []
        handler_error: List[BaseException] = []
        write_lock = threading.Lock()

        def pump_stdout() -> None:
            try:
                for line in stdout_pipe:
                    if line.startswith(INPUT_SENTINEL):
                        try:
                            prompt = json.loads(line[len(INPUT_SENTINEL):].strip())
                        except json.JSONDecodeError:
                            prompt = ""
                        if user_input_handler is None:
                            answer = ""
                        else:
                            try:
                                answer = str(user_input_handler(str(prompt)))
                            except BaseException as exc:  # noqa: BLE001 - report to parent
                                handler_error.append(exc)
                                _kill_process_tree(process)
                                return
                            answer = answer.replace("\n", " ").replace("\r", " ")
                        try:
                            with write_lock:
                                stdin_pipe.write(answer + "\n")
                                stdin_pipe.flush()
                        except (BrokenPipeError, OSError, ValueError):
                            return
                    else:
                        _append_capped(stdout_parts, line)
            except (ValueError, OSError):
                # Stream closed while shutting down
                pass

        def pump_stderr() -> None:
            try:
                for chunk in iter(lambda: stderr_pipe.read(4096), ""):
                    _append_capped(stderr_parts, chunk)
            except (ValueError, OSError):
                pass

        stdout_thread = threading.Thread(target=pump_stdout, daemon=True)
        stderr_thread = threading.Thread(target=pump_stderr, daemon=True)
        stdout_thread.start()
        stderr_thread.start()

        stdin_pipe.write(payload + "\n")
        stdin_pipe.flush()

        timed_out = False
        try:
            process.wait(timeout=self.config.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_process_tree(process)
            process.wait()
        finally:
            try:
                with write_lock:
                    stdin_pipe.close()
            except (OSError, ValueError):
                pass

        stdout_thread.join(timeout=2.0)
        stderr_thread.join(timeout=2.0)

        stdout = _truncate("".join(stdout_parts))
        stderr = _truncate("".join(stderr_parts))
        execution_time = time.time() - start_time

        if handler_error:
            return ExecutionResult(
                success=False,
                error_message=f"Input handler error: {handler_error[0]}",
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
            )

        if timed_out:
            return ExecutionResult(
                success=False,
                error_message=(
                    f"TimeoutError: execution exceeded "
                    f"{self.config.timeout_seconds} seconds"
                ),
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
            )

        if process.returncode == 0:
            return ExecutionResult(
                success=True,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
            )

        error_message = stderr.strip() or (
            f"Execution failed with exit code {process.returncode}"
        )
        return ExecutionResult(
            success=False,
            stdout=stdout,
            error_message=error_message,
            stderr=stderr,
            execution_time=execution_time,
        )

    def is_code_safe(self, python_code: str) -> Tuple[bool, str]:
        """
        Check if code is safe to execute without actually executing it.

        Returns:
            Tuple of (is_safe, reason).
        """
        safety_error = analyze_code(python_code, self.config)
        if safety_error is None:
            return True, "Code appears safe to execute"
        return False, safety_error

    def get_execution_warnings(self, python_code: str) -> List[str]:
        """
        Get warnings about potentially problematic code without executing it.

        Returns:
            List of warning messages.
        """
        warnings = []
        code_lower = python_code.lower()

        if "/" in python_code and "0" in python_code:
            warnings.append("Code contains division operations - check for division by zero")

        if "while true" in code_lower or "while 1" in code_lower:
            warnings.append("Code contains potential infinite loop")

        range_matches = re.findall(r"range\((\d+)\)", python_code)
        for match in range_matches:
            if int(match) > 10000:
                warnings.append(f"Large range operation detected: range({match})")

        lines = python_code.split("\n")
        defined_vars = set()
        for line in lines:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                var_name = line.split("=")[0].strip()
                if var_name.isidentifier():
                    defined_vars.add(var_name)

        var_usage = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", python_code)
        safe_builtins = {
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
            'getattr', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min',
            'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
            'str', 'sum', 'tuple', 'type', 'zip', 'input',
        }
        python_keywords = {
            'if', 'else', 'elif', 'for', 'while', 'def', 'class', 'return',
            'True', 'False', 'None', 'import', 'from', 'as', 'with', 'try',
            'except', 'finally', 'raise', 'pass', 'break', 'continue',
        }
        undefined_vars = set(var_usage) - defined_vars - safe_builtins - python_keywords

        if undefined_vars:
            warnings.append(
                f"Potentially undefined variables: {', '.join(sorted(undefined_vars))}"
            )

        return warnings


def _append_capped(parts: List[str], text: str) -> None:
    """Append text while keeping the total size under the capture cap."""
    current = sum(len(part) for part in parts)
    if current >= MAX_CAPTURE_CHARS:
        return
    room = MAX_CAPTURE_CHARS - current
    parts.append(text[:room])


def _truncate(text: str) -> str:
    if len(text) > MAX_CAPTURE_CHARS:
        return text[:MAX_CAPTURE_CHARS] + _TRUNCATION_MARKER
    return text


def _kill_process_tree(process: subprocess.Popen) -> None:
    """Kill the child process and, on Windows, its whole process tree."""
    if process.poll() is not None:
        return
    if sys.platform == "win32":
        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                creationflags=creationflags,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            pass
    try:
        process.kill()
    except OSError:
        pass
