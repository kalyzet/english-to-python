"""
Application Controller for English to Python Translator

Coordinates between GUI interface and backend services:
- Translation Engine
- Code Execution Service
- File operations
"""

import tkinter as tk
from typing import Optional
import os

try:
    from .main_window import MainWindow
    from ..services.translation_engine import TranslationEngine
    from ..services.code_execution_service import CodeExecutionService, ExecutionConfig
except (ImportError, ValueError):
    # Fallback for when running tests or direct imports
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    parent_dir = os.path.dirname(src_dir)
    
    for path in [src_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    try:
        from gui.main_window import MainWindow
        from services.translation_engine import TranslationEngine
        from services.code_execution_service import CodeExecutionService, ExecutionConfig
    except ImportError:
        # Last resort - try absolute imports
        import src.gui.main_window as mw
        import src.services.translation_engine as te
        import src.services.code_execution_service as ces
        
        MainWindow = mw.MainWindow
        TranslationEngine = te.TranslationEngine
        CodeExecutionService = ces.CodeExecutionService
        ExecutionConfig = ces.ExecutionConfig


class ApplicationController:
    """
    Main application controller that coordinates GUI and backend services
    """
    
    def __init__(self):
        """Initialize the application controller"""
        # Initialize backend services
        self.translation_engine = TranslationEngine()
        self.execution_service = CodeExecutionService(ExecutionConfig(
            timeout_seconds=30.0,
            allow_imports=False,
            allow_file_operations=False
        ))
        
        # Initialize GUI
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root)
        
        # Connect GUI callbacks to controller methods
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup GUI callbacks to controller methods"""
        self.main_window.set_translate_callback(self._handle_translate)
        self.main_window.set_run_callback(self._handle_run)
        self.main_window.set_save_callback(self._handle_save)
        self.main_window.set_load_callback(self._handle_load)
    
    def _handle_translate(self, english_text: str):
        """
        Handle translation request from GUI
        
        Args:
            english_text: English sentence to translate
            
        Returns:
            TranslationResult object for GUI to handle appropriately
        """
        try:
            # Update status to show translation is in progress
            self.main_window.set_status("Translating...")
            
            result = self.translation_engine.translate(english_text)
            
            # Update status based on result
            if result.success:
                self.main_window.set_status("Translation completed successfully")
            else:
                self.main_window.set_status("Translation failed")
            
            return result
                
        except Exception as e:
            # Create error result for unexpected exceptions
            self.main_window.set_status("Translation error occurred")
            from ..models.translation_result import TranslationResult
            return TranslationResult.create_error(
                f"Unexpected translation error: {str(e)}",
                english_text,
                0.0
            )
    
    def _handle_run(self, python_code: str):
        """
        Handle code execution request from GUI
        
        Args:
            python_code: Python code to execute
            
        Returns:
            ExecutionResult object for GUI to handle appropriately
        """
        try:
            # Update status to show execution is in progress
            self.main_window.set_status("Executing code...")
            
            # Set up input handler for interactive code
            def input_handler(prompt: str) -> str:
                # Use tkinter's simpledialog for user input
                import tkinter.simpledialog as simpledialog
                user_input = simpledialog.askstring("Input Required", prompt)
                return user_input if user_input is not None else ""
            
            # Execute the code
            result = self.execution_service.execute_code(python_code, input_handler)
            
            # Format the results for display
            if result.success:
                output_parts = ["=== Execution Successful ==="]
                if result.stdout:
                    output_parts.append("Output:")
                    output_parts.append(result.stdout)
                else:
                    output_parts.append("(No output produced)")
                
                # Add execution time
                output_parts.append(f"\nExecution time: {result.execution_time:.3f} seconds")
                
                # Add warnings if any
                warnings = self.execution_service.get_execution_warnings(python_code)
                if warnings:
                    output_parts.append("\nWarnings:")
                    for warning in warnings:
                        output_parts.append(f"- {warning}")
                
                # Update the result with formatted output
                result.output = "\n".join(output_parts)
                
                # Update status
                self.main_window.set_status("Code executed successfully")
            else:
                error_parts = ["=== Execution Failed ==="]
                if result.error_message:
                    error_parts.append("Error:")
                    error_parts.append(result.error_message)
                if result.stderr:
                    error_parts.append("Error Details:")
                    error_parts.append(result.stderr)
                
                # Add execution time
                error_parts.append(f"\nExecution time: {result.execution_time:.3f} seconds")
                
                # Update the result with formatted error message
                result.error_message = "\n".join(error_parts)
                
                # Update status
                self.main_window.set_status("Code execution failed")
            
            return result
            
        except Exception as e:
            # Create error result for unexpected exceptions
            self.main_window.set_status("Execution error occurred")
            from ..models.translation_result import ExecutionResult
            return ExecutionResult(
                success=False,
                output="",
                error_message=f"=== Execution Error ===\nUnexpected error: {str(e)}",
                execution_time=0.0
            )
    
    def _handle_save(self, code: str, file_path: str) -> bool:
        """
        Handle save file request from GUI
        
        Args:
            code: Python code to save
            file_path: Path to save file
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Update status to show save is in progress
            self.main_window.set_status("Saving file...")
            
            # Ensure the file has .py extension as per requirement 4.1
            if not file_path.lower().endswith('.py'):
                file_path += '.py'
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write the Python code to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Verify the file was written correctly
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                if saved_content == code:
                    self.main_window.set_status(f"File saved successfully: {os.path.basename(file_path)}")
                    return True
                else:
                    self.main_window.show_error("File was saved but content verification failed")
                    self.main_window.set_status("Save failed - verification error")
                    return False
            else:
                self.main_window.show_error("File was not created successfully")
                self.main_window.set_status("Save failed - file not created")
                return False
                
        except PermissionError:
            self.main_window.show_error(f"Permission denied: Cannot write to {file_path}")
            self.main_window.set_status("Save failed - permission denied")
            return False
        except OSError as e:
            self.main_window.show_error(f"File system error: {str(e)}")
            self.main_window.set_status("Save failed - file system error")
            return False
        except Exception as e:
            self.main_window.show_error(f"Failed to save file:\n{str(e)}")
            self.main_window.set_status("Save failed - unexpected error")
            return False
    
    def _handle_load(self, file_path: str) -> str:
        """
        Handle load file request from GUI
        
        Args:
            file_path: Path to file to load
            
        Returns:
            File content
            
        Raises:
            Exception: If file cannot be loaded
        """
        try:
            # Update status to show load is in progress
            self.main_window.set_status("Loading file...")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise Exception(f"File does not exist: {file_path}")
            
            # Check if it's a file (not a directory)
            if not os.path.isfile(file_path):
                raise Exception(f"Path is not a file: {file_path}")
            
            # Try to read the file with UTF-8 encoding first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # If UTF-8 fails, try with other common encodings
                encodings = ['latin-1', 'cp1252', 'iso-8859-1']
                content = None
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    raise Exception("Unable to decode file with any supported encoding")
            
            # Validate that the content is reasonable for English text input
            if len(content) > 100000:  # 100KB limit for text files
                raise Exception("File is too large (maximum 100KB for text input)")
            
            # Update status on successful load
            self.main_window.set_status(f"File loaded successfully: {os.path.basename(file_path)}")
            return content
            
        except PermissionError:
            self.main_window.set_status("Load failed - permission denied")
            raise Exception(f"Permission denied: Cannot read {file_path}")
        except OSError as e:
            self.main_window.set_status("Load failed - file system error")
            raise Exception(f"File system error: {str(e)}")
        except Exception as e:
            # Re-raise with more context if it's already our custom exception
            if "Failed to load file:" in str(e):
                self.main_window.set_status("Load failed")
                raise
            else:
                self.main_window.set_status("Load failed - unexpected error")
                raise Exception(f"Failed to load file: {str(e)}")
    
    def run(self):
        """Start the application"""
        try:
            # Handle application startup
            self.handle_application_startup()
            
            # Start the GUI main loop
            self.main_window.run()
            
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
        except Exception as e:
            print(f"Application error: {str(e)}")
        finally:
            # Handle application shutdown
            self.handle_application_shutdown()
    
    def get_main_window(self) -> MainWindow:
        """Get reference to main window for testing"""
        return self.main_window
    
    def get_translation_engine(self) -> TranslationEngine:
        """Get reference to translation engine for testing"""
        return self.translation_engine
    
    def get_execution_service(self) -> CodeExecutionService:
        """Get reference to execution service for testing"""
        return self.execution_service
    
    def handle_application_startup(self):
        """Handle application startup initialization"""
        try:
            # Initialize status
            self.main_window.set_status("English to Python Translator - Ready")
            
            # Clear any existing content
            self.main_window.clear_all()
            
            # Show welcome message in the input area
            welcome_message = ("Welcome to English to Python Translator!\n\n"
                             "Enter English instructions like:\n"
                             "• add 5 and 3\n"
                             "• set x to 10\n"
                             "• create list with 1, 2, 3\n"
                             "• if x greater than 5 then print yes\n\n"
                             "Then click 'Translate' to generate Python code.")
            
            self.main_window.set_input_text(welcome_message)
            
        except Exception as e:
            self.main_window.show_error(f"Startup error: {str(e)}")
            self.main_window.set_status("Startup error occurred")
    
    def handle_application_shutdown(self):
        """Handle application shutdown cleanup"""
        try:
            # Clear sensitive data
            self.main_window.clear_all()
            
            # Update status
            self.main_window.set_status("Shutting down...")
            
        except Exception as e:
            print(f"Shutdown error: {str(e)}")
    
    def handle_clear_all(self):
        """Handle clear all action"""
        try:
            self.main_window.clear_all()
            self.main_window.set_status("All fields cleared")
        except Exception as e:
            self.main_window.show_error(f"Clear error: {str(e)}")
            self.main_window.set_status("Clear failed")
    
    def get_application_info(self) -> dict:
        """Get information about the application state"""
        return {
            "translation_engine_ready": self.translation_engine is not None,
            "execution_service_ready": self.execution_service is not None,
            "gui_ready": self.main_window is not None,
            "supported_patterns": len(self.translation_engine.get_supported_patterns()) if self.translation_engine else 0
        }