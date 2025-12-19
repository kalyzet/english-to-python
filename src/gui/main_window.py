"""
Main GUI Window for English to Python Translator

Provides the main Tkinter-based GUI interface with:
- Input text area for English sentences
- Output text area for generated Python code with syntax highlighting
- Execution results area for code output
- Translate, Run, Save, and Load buttons
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from typing import Optional, Callable, List
import os
from .syntax_highlighter import PythonSyntaxHighlighter, CodeFormatter


class MainWindow:
    """
    Main GUI window for the English to Python Translator application
    
    Provides interface for:
    - Entering English sentences
    - Displaying generated Python code
    - Showing execution results
    - File operations (save/load)
    """
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        Initialize the main window
        
        Args:
            root: Tkinter root window, creates new if None
        """
        self.root = root if root is not None else tk.Tk()
        self.root.title("English to Python Translator")
        self.root.geometry("1000x700")
        
        # Callbacks for button actions (to be set by controller)
        self.translate_callback: Optional[Callable[[str], str]] = None
        self.run_callback: Optional[Callable[[str], str]] = None
        self.save_callback: Optional[Callable[[str, str], bool]] = None
        self.load_callback: Optional[Callable[[str], str]] = None
        
        # Syntax highlighter for Python code output
        self.syntax_highlighter: Optional[PythonSyntaxHighlighter] = None
        
        # Create GUI components
        self._create_widgets()
        self._layout_widgets()
        self._setup_syntax_highlighting()
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Title label
        self.title_label = tk.Label(
            self.root,
            text="English to Python Translator",
            font=("Arial", 16, "bold"),
            pady=10
        )
        
        # Input section
        self.input_label = tk.Label(
            self.root,
            text="English Input:",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        
        self.input_text = scrolledtext.ScrolledText(
            self.root,
            height=8,
            width=80,
            font=("Courier", 10),
            wrap=tk.WORD
        )
        
        # Button frame
        self.button_frame = tk.Frame(self.root)
        
        self.translate_button = tk.Button(
            self.button_frame,
            text="Translate",
            command=self._on_translate,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5
        )
        
        self.run_button = tk.Button(
            self.button_frame,
            text="Run Code",
            command=self._on_run,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=5
        )
        
        self.save_button = tk.Button(
            self.button_frame,
            text="Save Code",
            command=self._on_save,
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        
        self.load_button = tk.Button(
            self.button_frame,
            text="Load Input",
            command=self._on_load,
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        
        self.clear_button = tk.Button(
            self.button_frame,
            text="Clear All",
            command=self._on_clear,
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        
        self.format_button = tk.Button(
            self.button_frame,
            text="Format Code",
            command=self._on_format,
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        
        # Output section
        self.output_label = tk.Label(
            self.root,
            text="Generated Python Code:",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        
        self.output_text = scrolledtext.ScrolledText(
            self.root,
            height=10,
            width=80,
            font=("Courier", 10),
            wrap=tk.WORD,
            bg="#f5f5f5"
        )
        
        # Execution results section
        self.results_label = tk.Label(
            self.root,
            text="Execution Results:",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        
        self.results_text = scrolledtext.ScrolledText(
            self.root,
            height=6,
            width=80,
            font=("Courier", 10),
            wrap=tk.WORD,
            bg="#fffef0"
        )
        
        # Error display section (separate area for errors as per requirement 5.2)
        self.error_label = tk.Label(
            self.root,
            text="Errors and Warnings:",
            font=("Arial", 12, "bold"),
            anchor="w",
            fg="#d32f2f"
        )
        
        self.error_text = scrolledtext.ScrolledText(
            self.root,
            height=4,
            width=80,
            font=("Courier", 10),
            wrap=tk.WORD,
            bg="#ffebee",
            fg="#d32f2f"
        )
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor="w",
            font=("Arial", 9)
        )
    
    def _layout_widgets(self):
        """Layout all widgets using grid manager"""
        # Title
        self.title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Input section
        self.input_label.grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))
        self.input_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Buttons
        self.button_frame.grid(row=3, column=0, pady=10)
        self.translate_button.pack(side=tk.LEFT, padx=5)
        self.run_button.pack(side=tk.LEFT, padx=5)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.format_button.pack(side=tk.LEFT, padx=5)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Output section
        self.output_label.grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
        self.output_text.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
        
        # Results section
        self.results_label.grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))
        self.results_text.grid(row=7, column=0, sticky="nsew", padx=10, pady=5)
        
        # Error section
        self.error_label.grid(row=8, column=0, sticky="w", padx=10, pady=(10, 0))
        self.error_text.grid(row=9, column=0, sticky="nsew", padx=10, pady=5)
        
        # Status bar
        self.status_bar.grid(row=10, column=0, sticky="ew")
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(2, weight=2)  # Input area
        self.root.grid_rowconfigure(5, weight=3)  # Output area
        self.root.grid_rowconfigure(7, weight=2)  # Results area
        self.root.grid_rowconfigure(9, weight=1)  # Error area
        self.root.grid_columnconfigure(0, weight=1)
    
    def _setup_syntax_highlighting(self):
        """Setup syntax highlighting for the output text area"""
        # Initialize syntax highlighter for Python code output
        self.syntax_highlighter = PythonSyntaxHighlighter(self.output_text)
        
        # Enable automatic highlighting when text changes
        # Note: We don't enable auto-highlight by default to avoid performance issues
        # Highlighting is applied manually when setting output text
    
    def _on_translate(self):
        """Handle translate button click"""
        input_text = self.get_input_text()
        
        if not input_text.strip():
            self.display_translation_error("Please enter some English text to translate")
            return
        
        # Clear previous errors
        self.clear_error_text()
        self.set_status("Translating...")
        
        if self.translate_callback:
            try:
                result = self.translate_callback(input_text)
                # Check if result is a TranslationResult object or just a string
                if hasattr(result, 'success'):
                    # It's a TranslationResult object
                    if result.success:
                        self.set_output_text(result.python_code)
                        if result.warnings:
                            warning_text = "Warnings:\n" + "\n".join(result.warnings)
                            self.set_error_text(warning_text)
                        self.set_status("Translation complete")
                    else:
                        self.display_translation_error(result.error_message)
                        self.set_status("Translation failed")
                else:
                    # It's just a string (backward compatibility)
                    self.set_output_text(result)
                    self.set_status("Translation complete")
            except Exception as e:
                self.display_translation_error(f"Translation error: {str(e)}")
                self.set_status("Translation failed")
        else:
            self.display_translation_error("Translation service not configured")
            self.set_status("Ready")
    
    def _on_run(self):
        """Handle run button click"""
        code = self.get_output_text()
        
        if not code.strip():
            self.display_execution_error("No code to execute. Please translate some input first.")
            return
        
        self.set_status("Executing code...")
        
        if self.run_callback:
            try:
                result = self.run_callback(code)
                # Check if result is an ExecutionResult object or just a string
                if hasattr(result, 'success'):
                    # It's an ExecutionResult object
                    if result.success:
                        self.set_results_text(result.output)
                        self.set_status("Execution complete")
                    else:
                        self.display_execution_error(result.error_message)
                        self.set_status("Execution failed")
                else:
                    # It's just a string (backward compatibility)
                    self.set_results_text(result)
                    self.set_status("Execution complete")
            except Exception as e:
                self.display_execution_error(f"Execution error: {str(e)}")
                self.set_status("Execution failed")
        else:
            self.display_execution_error("Execution service not configured")
            self.set_status("Ready")
    
    def _on_save(self):
        """Handle save button click"""
        code = self.get_output_text()
        
        if not code.strip():
            self.show_error("No code to save. Please translate some input first.")
            return
        
        # Open file dialog with proper directory selection as per requirement 4.2
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                title="Save Python Code",
                initialdir=os.path.expanduser("~"),  # Start in user's home directory
                confirmoverwrite=True  # Ask for confirmation if file exists
            )
        except Exception as e:
            self.show_error(f"Error opening file dialog: {str(e)}")
            return
        
        if not file_path:
            return  # User cancelled
        
        self.set_status("Saving file...")
        
        if self.save_callback:
            try:
                success = self.save_callback(code, file_path)
                if success:
                    # Provide confirmation feedback as per requirement 4.3
                    self.show_info(f"Python code saved successfully to:\n{file_path}")
                    self.set_status(f"Saved to {os.path.basename(file_path)}")
                else:
                    self.show_error("Failed to save file")
                    self.set_status("Save failed")
            except Exception as e:
                self.show_error(f"Save error: {str(e)}")
                self.set_status("Save failed")
        else:
            # Default save implementation
            try:
                # Ensure .py extension as per requirement 4.1
                if not file_path.lower().endswith('.py'):
                    file_path += '.py'
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                # Provide confirmation feedback as per requirement 4.3
                self.show_info(f"Python code saved successfully to:\n{file_path}")
                self.set_status(f"Saved to {os.path.basename(file_path)}")
            except Exception as e:
                self.show_error(f"Save error: {str(e)}")
                self.set_status("Save failed")
    
    def _on_load(self):
        """Handle load button click"""
        # Open file dialog for loading English text files as per requirement 4.4
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All text files", "*.txt;*.md;*.rst"),
                    ("All files", "*.*")
                ],
                title="Load English Input",
                initialdir=os.path.expanduser("~")  # Start in user's home directory
            )
        except Exception as e:
            self.show_error(f"Error opening file dialog: {str(e)}")
            return
        
        if not file_path:
            return  # User cancelled
        
        self.set_status("Loading file...")
        
        if self.load_callback:
            try:
                content = self.load_callback(file_path)
                # Display content in input area as per requirement 4.5
                self.set_input_text(content)
                self.set_status(f"Loaded {os.path.basename(file_path)}")
                # Show confirmation that file was loaded
                self.show_info(f"English text loaded successfully from:\n{file_path}")
            except Exception as e:
                self.show_error(f"Load error: {str(e)}")
                self.set_status("Load failed")
        else:
            # Default load implementation
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Display content in input area as per requirement 4.5
                self.set_input_text(content)
                self.set_status(f"Loaded {os.path.basename(file_path)}")
                # Show confirmation that file was loaded
                self.show_info(f"English text loaded successfully from:\n{file_path}")
            except Exception as e:
                self.show_error(f"Load error: {str(e)}")
                self.set_status("Load failed")
    
    def _on_clear(self):
        """Handle clear button click"""
        self.clear_all()
        self.set_status("Cleared all fields")
    
    def _on_format(self):
        """Handle format code button click"""
        code = self.get_output_text()
        
        if not code.strip():
            self.show_info("No code to format. Please translate some input first.")
            return
        
        # Format and re-highlight the code
        self.set_output_text(code)
        self.set_status("Code formatted and highlighted")
    
    # Public methods for external control
    
    def get_input_text(self) -> str:
        """Get text from input area"""
        return self.input_text.get("1.0", tk.END).strip()
    
    def set_input_text(self, text: str):
        """Set text in input area"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", text)
    
    def get_output_text(self) -> str:
        """Get text from output area"""
        return self.output_text.get("1.0", tk.END).strip()
    
    def set_output_text(self, text: str):
        """Set text in output area with syntax highlighting and formatting"""
        # Format the code first
        formatted_text = CodeFormatter.format_python_code(text)
        
        # Clear and insert the formatted text
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", formatted_text)
        
        # Apply syntax highlighting
        if self.syntax_highlighter:
            self.syntax_highlighter.highlight_all()
    
    def get_results_text(self) -> str:
        """Get text from results area"""
        return self.results_text.get("1.0", tk.END).strip()
    
    def set_results_text(self, text: str):
        """Set text in results area"""
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", text)
    
    def get_error_text(self) -> str:
        """Get text from error area"""
        return self.error_text.get("1.0", tk.END).strip()
    
    def set_error_text(self, text: str):
        """Set text in error area"""
        self.error_text.delete("1.0", tk.END)
        self.error_text.insert("1.0", text)
    
    def append_error_text(self, text: str):
        """Append text to error area"""
        current_text = self.get_error_text()
        if current_text:
            new_text = current_text + "\n\n" + text
        else:
            new_text = text
        self.set_error_text(new_text)
    
    def clear_error_text(self):
        """Clear error area"""
        self.set_error_text("")
    
    def set_status(self, message: str):
        """Set status bar message"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def clear_all(self):
        """Clear all text areas"""
        self.set_input_text("")
        self.set_output_text("")
        self.set_results_text("")
        self.clear_error_text()
    
    def show_error(self, message: str):
        """Show error message dialog"""
        messagebox.showerror("Error", message)
    
    def show_info(self, message: str):
        """Show info message dialog"""
        messagebox.showinfo("Information", message)
    
    def show_warning(self, message: str):
        """Show warning message dialog"""
        messagebox.showwarning("Warning", message)
    
    def display_translation_error(self, error_message: str):
        """Display translation error in the dedicated error area (Requirement 5.2)"""
        timestamp = self._get_timestamp()
        formatted_error = f"[{timestamp}] TRANSLATION ERROR:\n{error_message}"
        self.set_error_text(formatted_error)
    
    def display_execution_error(self, error_message: str):
        """Display execution error in the dedicated error area"""
        timestamp = self._get_timestamp()
        formatted_error = f"[{timestamp}] EXECUTION ERROR:\n{error_message}"
        self.append_error_text(formatted_error)
    
    def display_validation_error(self, error_message: str, examples: List[str] = None):
        """Display validation error with examples (Requirement 5.5)"""
        timestamp = self._get_timestamp()
        formatted_error = f"[{timestamp}] INPUT ERROR:\n{error_message}"
        
        if examples:
            formatted_error += "\n\nValid examples:\n"
            for i, example in enumerate(examples, 1):
                formatted_error += f"{i}. {example}\n"
        
        self.set_error_text(formatted_error)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for error messages"""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def set_translate_callback(self, callback: Callable[[str], str]):
        """Set callback for translate button"""
        self.translate_callback = callback
    
    def set_run_callback(self, callback: Callable[[str], str]):
        """Set callback for run button"""
        self.run_callback = callback
    
    def set_save_callback(self, callback: Callable[[str, str], bool]):
        """Set callback for save button"""
        self.save_callback = callback
    
    def set_load_callback(self, callback: Callable[[str], str]):
        """Set callback for load button"""
        self.load_callback = callback
    
    def refresh_syntax_highlighting(self):
        """Manually refresh syntax highlighting for output area"""
        if self.syntax_highlighter:
            self.syntax_highlighter.highlight_all()
    
    def enable_auto_highlighting(self):
        """Enable automatic syntax highlighting on text changes"""
        if self.syntax_highlighter:
            self.syntax_highlighter.enable_auto_highlight()
    
    def disable_auto_highlighting(self):
        """Disable automatic syntax highlighting"""
        if self.syntax_highlighter:
            self.syntax_highlighter.disable_auto_highlight()
    
    def format_output_code(self):
        """Format the code in the output area"""
        current_code = self.get_output_text()
        if current_code.strip():
            self.set_output_text(current_code)
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()
    
    def destroy(self):
        """Destroy the window"""
        self.root.destroy()
