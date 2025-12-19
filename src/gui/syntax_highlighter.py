"""
Python Syntax Highlighter for Tkinter Text Widget

Provides syntax highlighting for Python code using Tkinter Text widget tags.
Supports highlighting of keywords, strings, comments, numbers, and operators.
"""

import tkinter as tk
import re
from typing import Dict, List, Tuple


class PythonSyntaxHighlighter:
    """
    Python syntax highlighter for Tkinter Text widgets
    
    Uses regular expressions to identify Python syntax elements and applies
    appropriate color formatting using Text widget tags.
    """
    
    def __init__(self, text_widget: tk.Text):
        """
        Initialize the syntax highlighter
        
        Args:
            text_widget: Tkinter Text widget to apply highlighting to
        """
        self.text_widget = text_widget
        self._setup_tags()
        self._setup_patterns()
    
    def _setup_tags(self):
        """Setup text tags for different syntax elements"""
        # Define color scheme for Python syntax highlighting
        self.text_widget.tag_configure("keyword", foreground="#0000FF", font=("Courier", 10, "bold"))
        self.text_widget.tag_configure("builtin", foreground="#800080", font=("Courier", 10))
        self.text_widget.tag_configure("string", foreground="#008000", font=("Courier", 10))
        self.text_widget.tag_configure("comment", foreground="#808080", font=("Courier", 10, "italic"))
        self.text_widget.tag_configure("number", foreground="#FF6600", font=("Courier", 10))
        self.text_widget.tag_configure("operator", foreground="#000000", font=("Courier", 10, "bold"))
        self.text_widget.tag_configure("function", foreground="#0066CC", font=("Courier", 10))
        self.text_widget.tag_configure("class", foreground="#CC0066", font=("Courier", 10, "bold"))
        self.text_widget.tag_configure("decorator", foreground="#666600", font=("Courier", 10))
        self.text_widget.tag_configure("normal", foreground="#000000", font=("Courier", 10))
    
    def _setup_patterns(self):
        """Setup regular expression patterns for syntax elements"""
        # Python keywords
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'class', 
            'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 
            'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 
            'while', 'with', 'yield'
        ]
        
        # Python built-in functions
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir', 'enumerate',
            'eval', 'exec', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int',
            'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals', 'map',
            'max', 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print',
            'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip'
        ]
        
        # Compile patterns for better performance
        self.patterns = [
            # Comments (must be first to avoid conflicts)
            (r'#.*$', 'comment'),
            
            # Triple-quoted strings (multiline)
            (r'""".*?"""', 'string'),
            (r"'''.*?'''", 'string'),
            
            # Regular strings
            (r'"[^"\\]*(\\.[^"\\]*)*"', 'string'),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 'string'),
            
            # Raw strings
            (r'r"[^"\\]*(\\.[^"\\]*)*"', 'string'),
            (r"r'[^'\\]*(\\.[^'\\]*)*'", 'string'),
            
            # f-strings
            (r'f"[^"\\]*(\\.[^"\\]*)*"', 'string'),
            (r"f'[^'\\]*(\\.[^'\\]*)*'", 'string'),
            
            # Decorators
            (r'@\w+', 'decorator'),
            
            # Class definitions
            (r'\bclass\s+\w+', 'class'),
            
            # Function definitions
            (r'\bdef\s+\w+', 'function'),
            
            # Numbers (integers, floats, scientific notation)
            (r'\b\d+\.?\d*([eE][+-]?\d+)?\b', 'number'),
            (r'\b0[xX][0-9a-fA-F]+\b', 'number'),  # Hexadecimal
            (r'\b0[oO][0-7]+\b', 'number'),        # Octal
            (r'\b0[bB][01]+\b', 'number'),         # Binary
            
            # Keywords
            (r'\b(' + '|'.join(keywords) + r')\b', 'keyword'),
            
            # Built-in functions
            (r'\b(' + '|'.join(builtins) + r')\b', 'builtin'),
            
            # Operators
            (r'[+\-*/%=<>!&|^~]', 'operator'),
            (r'[(){}[\],.:;]', 'operator'),
        ]
        
        # Compile all patterns for better performance
        self.compiled_patterns = [
            (re.compile(pattern, re.MULTILINE | re.DOTALL), tag)
            for pattern, tag in self.patterns
        ]
    
    def highlight_all(self):
        """Apply syntax highlighting to all text in the widget"""
        # Get all text content
        content = self.text_widget.get("1.0", tk.END)
        
        # Remove all existing tags
        for tag in ["keyword", "builtin", "string", "comment", "number", 
                   "operator", "function", "class", "decorator", "normal"]:
            self.text_widget.tag_remove(tag, "1.0", tk.END)
        
        # Apply highlighting patterns
        for pattern, tag in self.compiled_patterns:
            self._highlight_pattern(content, pattern, tag)
    
    def _highlight_pattern(self, content: str, pattern: re.Pattern, tag: str):
        """
        Apply highlighting for a specific pattern
        
        Args:
            content: Text content to search in
            pattern: Compiled regular expression pattern
            tag: Tag name to apply
        """
        for match in pattern.finditer(content):
            start_pos = self._get_text_position(content, match.start())
            end_pos = self._get_text_position(content, match.end())
            
            # Apply the tag to the matched text
            self.text_widget.tag_add(tag, start_pos, end_pos)
    
    def _get_text_position(self, content: str, char_index: int) -> str:
        """
        Convert character index to Tkinter text position (line.column)
        
        Args:
            content: Full text content
            char_index: Character index in the content
            
        Returns:
            Tkinter text position string (e.g., "1.0", "2.5")
        """
        lines_before = content[:char_index].count('\n')
        line_start = content.rfind('\n', 0, char_index) + 1
        column = char_index - line_start
        
        return f"{lines_before + 1}.{column}"
    
    def highlight_range(self, start: str, end: str):
        """
        Apply syntax highlighting to a specific range of text
        
        Args:
            start: Start position (e.g., "1.0")
            end: End position (e.g., "1.10")
        """
        # Get text in the specified range
        content = self.text_widget.get(start, end)
        
        # Remove existing tags in the range
        for tag in ["keyword", "builtin", "string", "comment", "number", 
                   "operator", "function", "class", "decorator", "normal"]:
            self.text_widget.tag_remove(tag, start, end)
        
        # Apply highlighting patterns to the range
        for pattern, tag in self.compiled_patterns:
            for match in pattern.finditer(content):
                # Calculate absolute positions
                match_start = self._add_positions(start, f"0.{match.start()}")
                match_end = self._add_positions(start, f"0.{match.end()}")
                
                # Apply the tag
                self.text_widget.tag_add(tag, match_start, match_end)
    
    def _add_positions(self, pos1: str, pos2: str) -> str:
        """
        Add two Tkinter text positions
        
        Args:
            pos1: First position (e.g., "1.5")
            pos2: Second position (e.g., "0.3")
            
        Returns:
            Sum of positions
        """
        line1, col1 = map(int, pos1.split('.'))
        line2, col2 = map(int, pos2.split('.'))
        
        return f"{line1 + line2}.{col1 + col2}"
    
    def format_code(self, code: str) -> str:
        """
        Format Python code with proper indentation
        
        Args:
            code: Python code string to format
            
        Returns:
            Formatted Python code
        """
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for certain keywords
            if stripped.startswith(('except', 'elif', 'else', 'finally')):
                current_indent = max(0, indent_level - 1)
            elif stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
                current_indent = indent_level
            else:
                current_indent = indent_level
            
            # Add the formatted line
            formatted_lines.append('    ' * current_indent + stripped)
            
            # Increase indent after certain keywords
            if stripped.endswith(':') and any(stripped.startswith(kw) for kw in 
                ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 
                 'with', 'def', 'class']):
                indent_level += 1
            
            # Decrease indent after certain statements
            if stripped in ['pass', 'break', 'continue'] or stripped.startswith('return'):
                if indent_level > 0:
                    indent_level -= 1
        
        return '\n'.join(formatted_lines)
    
    def enable_auto_highlight(self):
        """Enable automatic highlighting on text changes"""
        def on_text_change(event=None):
            # Schedule highlighting after a short delay to avoid performance issues
            self.text_widget.after_idle(self.highlight_all)
        
        # Bind to text modification events
        self.text_widget.bind('<KeyRelease>', on_text_change)
        self.text_widget.bind('<Button-1>', on_text_change)
        self.text_widget.bind('<ButtonRelease-1>', on_text_change)
    
    def disable_auto_highlight(self):
        """Disable automatic highlighting"""
        self.text_widget.unbind('<KeyRelease>')
        self.text_widget.unbind('<Button-1>')
        self.text_widget.unbind('<ButtonRelease-1>')


class CodeFormatter:
    """
    Python code formatter for proper indentation and structure
    """
    
    @staticmethod
    def format_python_code(code: str) -> str:
        """
        Format Python code with proper indentation and structure
        
        Args:
            code: Raw Python code string
            
        Returns:
            Formatted Python code with proper indentation
        """
        if not code.strip():
            return code
        
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines but preserve them
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Handle dedent keywords
            if any(stripped.startswith(kw) for kw in ['except', 'elif', 'else', 'finally']):
                if indent_level > 0:
                    indent_level -= 1
            
            # Add properly indented line
            formatted_lines.append('    ' * indent_level + stripped)
            
            # Handle indent keywords
            if stripped.endswith(':'):
                if any(stripped.startswith(kw) for kw in 
                      ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 
                       'finally', 'with', 'def', 'class']):
                    indent_level += 1
            
            # Handle special cases that might reduce indentation
            if stripped in ['pass', 'break', 'continue'] or stripped.startswith('return'):
                # These statements often end a block, but we'll let the next line determine indentation
                pass
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def clean_code(code: str) -> str:
        """
        Clean up code by removing extra whitespace and normalizing line endings
        
        Args:
            code: Raw code string
            
        Returns:
            Cleaned code string
        """
        # Normalize line endings
        code = code.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in code.split('\n')]
        
        # Remove excessive blank lines (more than 2 consecutive)
        cleaned_lines = []
        blank_count = 0
        
        for line in lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:  # Allow up to 2 consecutive blank lines
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)