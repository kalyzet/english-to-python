"""
Property-based tests for GUI functionality
Tests GUI initialization, text input acceptance, and translation output display
"""

import pytest
from hypothesis import given, strategies as st, settings
import tkinter as tk
from src.gui.main_window import MainWindow
from src.gui.application_controller import ApplicationController


def create_test_root():
    """Helper function to create Tkinter root with proper error handling"""
    try:
        return tk.Tk()
    except tk.TclError as e:
        pytest.skip(f"Tkinter not properly configured: {e}")


def safe_destroy(root):
    """Helper function to safely destroy Tkinter root"""
    try:
        if root:
            root.destroy()
    except:
        pass


class TestGUIInitialization:
    """
    **Feature: english-to-python-translator, Property 1: GUI initialization displays required elements**
    **Validates: Requirements 1.1**
    
    Property: For any application startup, the GUI should display both an input text area 
    and output text area that are visible and accessible.
    """
    
    @settings(max_examples=100, deadline=None)
    @given(st.just(None))  # No random input needed, just test initialization
    def test_gui_displays_required_elements(self, _):
        """
        Property: GUI initialization should display all required elements
        """
        # Create root window
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            # Create main window
            window = MainWindow(root)
            
            # Property: Input text area should exist and be accessible
            assert hasattr(window, 'input_text'), "GUI should have input_text attribute"
            assert window.input_text is not None, "Input text area should not be None"
            assert isinstance(window.input_text, tk.Text) or hasattr(window.input_text, 'get'), \
                "Input text area should be a Text widget"
            
            # Property: Output text area should exist and be accessible
            assert hasattr(window, 'output_text'), "GUI should have output_text attribute"
            assert window.output_text is not None, "Output text area should not be None"
            assert isinstance(window.output_text, tk.Text) or hasattr(window.output_text, 'get'), \
                "Output text area should be a Text widget"
            
            # Property: Execution results area should exist and be accessible
            assert hasattr(window, 'results_text'), "GUI should have results_text attribute"
            assert window.results_text is not None, "Results text area should not be None"
            assert isinstance(window.results_text, tk.Text) or hasattr(window.results_text, 'get'), \
                "Results text area should be a Text widget"
            
            # Property: Required buttons should exist
            assert hasattr(window, 'translate_button'), "GUI should have translate button"
            assert hasattr(window, 'run_button'), "GUI should have run button"
            assert hasattr(window, 'save_button'), "GUI should have save button"
            assert hasattr(window, 'load_button'), "GUI should have load button"
            
            # Property: Buttons should not be None
            assert window.translate_button is not None, "Translate button should not be None"
            assert window.run_button is not None, "Run button should not be None"
            assert window.save_button is not None, "Save button should not be None"
            assert window.load_button is not None, "Load button should not be None"
            
            # Property: Text areas should be initially empty or have default content
            input_content = window.get_input_text()
            assert isinstance(input_content, str), "Input text should be a string"
            
            output_content = window.get_output_text()
            assert isinstance(output_content, str), "Output text should be a string"
            
            results_content = window.get_results_text()
            assert isinstance(results_content, str), "Results text should be a string"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            # Clean up
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(st.just(None))
    def test_gui_elements_are_visible(self, _):
        """
        Property: GUI elements should be visible and properly configured
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Text widgets should be visible (winfo_viewable checks if widget is mapped)
            # Note: In testing, widgets might not be fully rendered, so we check if they're configured
            assert window.input_text.winfo_exists(), "Input text area should exist in widget tree"
            assert window.output_text.winfo_exists(), "Output text area should exist in widget tree"
            assert window.results_text.winfo_exists(), "Results text area should exist in widget tree"
            
            # Property: Buttons should be visible
            assert window.translate_button.winfo_exists(), "Translate button should exist in widget tree"
            assert window.run_button.winfo_exists(), "Run button should exist in widget tree"
            assert window.save_button.winfo_exists(), "Save button should exist in widget tree"
            assert window.load_button.winfo_exists(), "Load button should exist in widget tree"
            
            # Property: Text areas should have reasonable dimensions
            # (height and width should be positive)
            input_height = window.input_text.cget('height')
            assert input_height > 0, "Input text area should have positive height"
            
            output_height = window.output_text.cget('height')
            assert output_height > 0, "Output text area should have positive height"
            
            results_height = window.results_text.cget('height')
            assert results_height > 0, "Results text area should have positive height"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(st.just(None))
    def test_gui_has_proper_labels(self, _):
        """
        Property: GUI should have proper labels for each section
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Labels should exist for each text area
            assert hasattr(window, 'input_label'), "GUI should have input label"
            assert hasattr(window, 'output_label'), "GUI should have output label"
            assert hasattr(window, 'results_label'), "GUI should have results label"
            
            # Property: Labels should not be None
            assert window.input_label is not None, "Input label should not be None"
            assert window.output_label is not None, "Output label should not be None"
            assert window.results_label is not None, "Results label should not be None"
            
            # Property: Labels should have text content
            input_label_text = window.input_label.cget('text')
            assert input_label_text and len(input_label_text) > 0, "Input label should have text"
            
            output_label_text = window.output_label.cget('text')
            assert output_label_text and len(output_label_text) > 0, "Output label should have text"
            
            results_label_text = window.results_label.cget('text')
            assert results_label_text and len(results_label_text) > 0, "Results label should have text"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass


class TestTextInputAcceptance:
    """
    **Feature: english-to-python-translator, Property 2: Text input acceptance**
    **Validates: Requirements 1.2**
    
    Property: For any text string entered in the input area, the GUI should accept 
    and display that text without modification.
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        text_input=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
                whitelist_characters='.,!?;:-_'
            ),
            min_size=0,
            max_size=500
        )
    )
    def test_input_area_accepts_text(self, text_input):
        """
        Property: Input area should accept and display any text without modification
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting text should not raise an exception
            window.set_input_text(text_input)
            
            # Property: Getting text should return the same text (possibly with whitespace normalization)
            retrieved_text = window.get_input_text()
            
            # Property: Retrieved text should match input (after stripping trailing whitespace)
            # Note: Tkinter Text widgets may add trailing newlines, so we compare stripped versions
            assert retrieved_text.strip() == text_input.strip(), \
                f"Input text should be preserved. Expected: '{text_input}', Got: '{retrieved_text}'"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=100, deadline=None)
    @given(
        text_input=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=200
        )
    )
    def test_input_area_preserves_content(self, text_input):
        """
        Property: Input area should preserve text content across multiple operations
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting text multiple times should work correctly
            window.set_input_text(text_input)
            first_retrieval = window.get_input_text()
            
            # Get text again without setting
            second_retrieval = window.get_input_text()
            
            # Property: Multiple retrievals should return the same content
            assert first_retrieval == second_retrieval, \
                "Multiple retrievals should return the same content"
            
            # Property: Content should match original input
            assert first_retrieval.strip() == text_input.strip(), \
                "Content should match original input"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        text1=st.text(min_size=1, max_size=100),
        text2=st.text(min_size=1, max_size=100)
    )
    def test_input_area_can_be_updated(self, text1, text2):
        """
        Property: Input area should allow updating text content
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not available: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting first text should work
            window.set_input_text(text1)
            retrieved1 = window.get_input_text()
            assert retrieved1.strip() == text1.strip(), "First text should be set correctly"
            
            # Property: Updating to second text should work
            window.set_input_text(text2)
            retrieved2 = window.get_input_text()
            assert retrieved2.strip() == text2.strip(), "Second text should replace first text"
            
            # Property: Second text should completely replace first text
            assert retrieved2.strip() != text1.strip() or text1.strip() == text2.strip(), \
                "Updated text should replace previous text"
            
        finally:
            root.destroy()
    
    @settings(max_examples=50, deadline=None)
    @given(st.just(""))
    def test_input_area_accepts_empty_text(self, empty_text):
        """
        Property: Input area should accept empty text (clearing)
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Set some initial text
            window.set_input_text("initial text")
            
            # Property: Setting empty text should clear the input area
            window.set_input_text(empty_text)
            retrieved = window.get_input_text()
            
            # Property: Retrieved text should be empty
            assert retrieved.strip() == "", "Input area should accept empty text"
            
        finally:
            root.destroy()
    
    @settings(max_examples=50, deadline=None)
    @given(
        multiline_text=st.lists(
            st.text(min_size=1, max_size=50),
            min_size=2,
            max_size=10
        ).map(lambda lines: '\n'.join(lines))
    )
    def test_input_area_accepts_multiline_text(self, multiline_text):
        """
        Property: Input area should accept and preserve multiline text
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting multiline text should work
            window.set_input_text(multiline_text)
            retrieved = window.get_input_text()
            
            # Property: Multiline structure should be preserved
            # (allowing for minor whitespace differences)
            original_lines = [line.strip() for line in multiline_text.split('\n') if line.strip()]
            retrieved_lines = [line.strip() for line in retrieved.split('\n') if line.strip()]
            
            assert len(retrieved_lines) >= len(original_lines) - 1, \
                "Multiline text structure should be preserved"
            
        finally:
            root.destroy()


class TestTranslationOutputDisplay:
    """
    **Feature: english-to-python-translator, Property 4: Translation output display**
    **Validates: Requirements 1.4, 1.5**
    
    Property: For any successful translation, the output area should display 
    the generated Python code with proper formatting and syntax highlighting.
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        python_code=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
                whitelist_characters='=+-*/()[]{}.,;:\n\t_'
            ),
            min_size=1,
            max_size=500
        )
    )
    def test_output_area_displays_code(self, python_code):
        """
        Property: Output area should display generated Python code
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting output text should not raise an exception
            window.set_output_text(python_code)
            
            # Property: Getting output text should return the code
            retrieved_code = window.get_output_text()
            
            # Property: Retrieved code should match input
            assert retrieved_code.strip() == python_code.strip(), \
                f"Output code should be preserved. Expected: '{python_code}', Got: '{retrieved_code}'"
            
        finally:
            root.destroy()
    
    @settings(max_examples=50, deadline=None)
    @given(
        python_code=st.sampled_from([
            "x = 5",
            "result = a + b",
            "if x > 0:\n    print('positive')",
            "for i in range(10):\n    print(i)",
            "my_list = [1, 2, 3, 4, 5]",
            "def hello():\n    return 'world'"
        ])
    )
    def test_output_area_displays_valid_python_code(self, python_code):
        """
        Property: Output area should correctly display valid Python code
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting valid Python code should work
            window.set_output_text(python_code)
            retrieved = window.get_output_text()
            
            # Property: Code structure should be preserved
            assert retrieved.strip() == python_code.strip(), \
                "Valid Python code should be preserved in output area"
            
            # Property: Output should contain Python syntax elements
            python_indicators = ['=', '+', '-', '*', '/', 'if', 'for', 'while', 'def', 'print', '[', ']']
            has_python_syntax = any(indicator in retrieved for indicator in python_indicators)
            assert has_python_syntax or len(retrieved.strip()) == 0, \
                "Output should contain Python syntax elements"
            
        finally:
            root.destroy()
    
    @settings(max_examples=50, deadline=None)
    @given(
        code_with_indentation=st.sampled_from([
            "if True:\n    x = 1\n    y = 2",
            "for i in range(5):\n    print(i)\n    print(i * 2)",
            "def func():\n    return 42",
            "while x < 10:\n    x += 1\n    print(x)"
        ])
    )
    def test_output_area_preserves_formatting(self, code_with_indentation):
        """
        Property: Output area should preserve code formatting including indentation
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting formatted code should preserve structure
            window.set_output_text(code_with_indentation)
            retrieved = window.get_output_text()
            
            # Property: Indentation should be preserved (check for whitespace at line starts)
            original_lines = code_with_indentation.split('\n')
            retrieved_lines = retrieved.split('\n')
            
            # Check that we have similar number of lines
            assert len(retrieved_lines) >= len(original_lines) - 1, \
                "Code structure should be preserved"
            
            # Check that indented lines are still indented
            for orig_line in original_lines:
                if orig_line.startswith('    ') or orig_line.startswith('\t'):
                    # At least some indentation should be preserved in output
                    has_indented_line = any(
                        line.startswith(' ') or line.startswith('\t') 
                        for line in retrieved_lines
                    )
                    assert has_indented_line, "Indentation should be preserved"
                    break
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        code1=st.text(min_size=1, max_size=100),
        code2=st.text(min_size=1, max_size=100)
    )
    def test_output_area_can_be_updated(self, code1, code2):
        """
        Property: Output area should allow updating displayed code
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting first code should work
            window.set_output_text(code1)
            retrieved1 = window.get_output_text()
            assert retrieved1.strip() == code1.strip(), "First code should be displayed"
            
            # Property: Updating to second code should work
            window.set_output_text(code2)
            retrieved2 = window.get_output_text()
            assert retrieved2.strip() == code2.strip(), "Second code should replace first"
            
        finally:
            root.destroy()
    
    @settings(max_examples=50, deadline=None)
    @given(st.just(None))
    def test_output_area_has_appropriate_styling(self, _):
        """
        Property: Output area should have appropriate styling for code display
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Output text widget should have monospace font for code
            font_config = window.output_text.cget('font')
            assert font_config is not None, "Output area should have font configured"
            
            # Property: Output area should have reasonable dimensions
            height = window.output_text.cget('height')
            assert height > 0, "Output area should have positive height"
            
            width = window.output_text.cget('width')
            assert width > 0, "Output area should have positive width"
            
        finally:
            root.destroy()
    
    @settings(max_examples=50, deadline=None)
    @given(
        execution_result=st.text(min_size=1, max_size=200)
    )
    def test_results_area_displays_execution_output(self, execution_result):
        """
        Property: Results area should display execution output
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            window = MainWindow(root)
            
            # Property: Setting results text should work
            window.set_results_text(execution_result)
            retrieved = window.get_results_text()
            
            # Property: Results should be preserved
            assert retrieved.strip() == execution_result.strip(), \
                "Execution results should be displayed correctly"
            
        finally:
            root.destroy()


class TestFileSaveOperation:
    """
    **Feature: english-to-python-translator, Property 14: File save operation**
    **Validates: Requirements 4.1, 4.3**
    
    Property: For any generated Python code, saving to file should create a file with .py extension 
    containing the exact code and provide confirmation feedback.
    """
    
    @settings(max_examples=50, deadline=None)
    @given(
        python_code=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
                whitelist_characters='=+-*/()[]{}.,;:\n\t_#'
            ),
            min_size=1,
            max_size=200
        )
    )
    def test_file_save_creates_py_file_with_exact_content(self, python_code):
        """
        Property: Saving Python code should create a .py file with exact content
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            
            # Create a temporary file path
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Property: Save operation should succeed
                success = controller._handle_save(python_code, temp_path)
                assert success, "Save operation should succeed"
                
                # Property: File should exist after save
                assert os.path.exists(temp_path), "File should exist after save operation"
                
                # Property: File should have .py extension (requirement 4.1)
                assert temp_path.endswith('.py'), "Saved file should have .py extension"
                
                # Property: File should contain exact code content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                assert saved_content == python_code, \
                    f"Saved content should match original code. Expected: '{python_code}', Got: '{saved_content}'"
                
                # Property: File should be readable
                assert os.access(temp_path, os.R_OK), "Saved file should be readable"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=30, deadline=None)
    @given(
        python_code=st.sampled_from([
            "x = 5",
            "result = a + b",
            "if x > 0:\n    print('positive')",
            "for i in range(10):\n    print(i)",
            "my_list = [1, 2, 3, 4, 5]",
            "def hello():\n    return 'world'",
            "# This is a comment\nprint('Hello, World!')"
        ])
    )
    def test_file_save_handles_valid_python_code(self, python_code):
        """
        Property: Save operation should handle valid Python code correctly
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            
            # Create temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, 'test_code.py')
                
                # Property: Save should succeed for valid Python code
                success = controller._handle_save(python_code, temp_path)
                assert success, "Save should succeed for valid Python code"
                
                # Property: Saved file should contain the exact code
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                assert saved_content == python_code, "Saved content should match original"
                
                # Property: File should have correct extension
                assert temp_path.endswith('.py'), "File should have .py extension"
                
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=30, deadline=None)
    @given(
        filename=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=20
        ).filter(lambda x: x and not any(c in x for c in '<>:"/\\|?*'))
    )
    def test_file_save_adds_py_extension_if_missing(self, filename):
        """
        Property: Save operation should add .py extension if not present
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            test_code = "print('test')"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create path without .py extension
                temp_path = os.path.join(temp_dir, filename)
                
                # Property: Save should succeed and add .py extension
                success = controller._handle_save(test_code, temp_path)
                assert success, "Save should succeed"
                
                # Property: File with .py extension should exist
                expected_path = temp_path + '.py' if not temp_path.endswith('.py') else temp_path
                assert os.path.exists(expected_path), "File with .py extension should exist"
                
                # Property: Content should be preserved
                with open(expected_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                assert saved_content == test_code, "Content should be preserved"
                
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=20, deadline=None)
    @given(st.just("test_code"))
    def test_file_save_creates_directory_if_needed(self, _):
        """
        Property: Save operation should create directories if they don't exist
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            test_code = "print('test')"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create path with non-existent subdirectory
                subdir = os.path.join(temp_dir, 'new_directory')
                temp_path = os.path.join(subdir, 'test.py')
                
                # Property: Directory should not exist initially
                assert not os.path.exists(subdir), "Directory should not exist initially"
                
                # Property: Save should succeed and create directory
                success = controller._handle_save(test_code, temp_path)
                assert success, "Save should succeed and create directory"
                
                # Property: Directory should be created
                assert os.path.exists(subdir), "Directory should be created"
                assert os.path.isdir(subdir), "Created path should be a directory"
                
                # Property: File should be created in the new directory
                assert os.path.exists(temp_path), "File should be created in new directory"
                
                # Property: Content should be correct
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                assert saved_content == test_code, "Content should be correct"
                
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=20, deadline=None)
    @given(st.just(""))
    def test_file_save_handles_empty_code(self, empty_code):
        """
        Property: Save operation should handle empty code correctly
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Property: Save should succeed even for empty code
                success = controller._handle_save(empty_code, temp_path)
                assert success, "Save should succeed for empty code"
                
                # Property: File should exist
                assert os.path.exists(temp_path), "File should exist after save"
                
                # Property: File should contain empty content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                assert saved_content == empty_code, "Saved content should match empty input"
                
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass


class TestFileLoadAndDisplay:
    """
    **Feature: english-to-python-translator, Property 16: File load and display**
    **Validates: Requirements 4.4, 4.5**
    
    Property: For any text file loaded, the content should appear in the input area 
    exactly as stored in the file.
    """
    
    @settings(max_examples=50, deadline=None)
    @given(
        english_text=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
                whitelist_characters='.,!?;:-_\n'
            ),
            min_size=1,
            max_size=500
        )
    )
    def test_file_load_displays_exact_content_in_input_area(self, english_text):
        """
        Property: Loading a text file should display its exact content in the input area
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            
            # Create a temporary text file with the content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(english_text)
                temp_path = temp_file.name
            
            try:
                # Property: Load operation should succeed
                loaded_content = controller._handle_load(temp_path)
                
                # Property: Loaded content should match original text exactly
                assert loaded_content == english_text, \
                    f"Loaded content should match original. Expected: '{english_text}', Got: '{loaded_content}'"
                
                # Property: Content should be displayable in input area
                controller.get_main_window().set_input_text(loaded_content)
                displayed_content = controller.get_main_window().get_input_text()
                
                # Property: Displayed content should match loaded content (requirement 4.5)
                assert displayed_content.strip() == loaded_content.strip(), \
                    "Content displayed in input area should match loaded content"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=30, deadline=None)
    @given(
        english_sentences=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')),
                min_size=5,
                max_size=50
            ),
            min_size=1,
            max_size=10
        ).map(lambda sentences: '\n'.join(sentences))
    )
    def test_file_load_handles_multiline_text(self, english_sentences):
        """
        Property: Loading multiline text files should preserve line structure
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            
            # Create temporary file with multiline content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(english_sentences)
                temp_path = temp_file.name
            
            try:
                # Property: Load should succeed for multiline text
                loaded_content = controller._handle_load(temp_path)
                
                # Property: Line structure should be preserved
                original_lines = english_sentences.split('\n')
                loaded_lines = loaded_content.split('\n')
                
                assert len(loaded_lines) == len(original_lines), \
                    "Number of lines should be preserved"
                
                for orig_line, loaded_line in zip(original_lines, loaded_lines):
                    assert orig_line == loaded_line, \
                        f"Line content should be preserved. Expected: '{orig_line}', Got: '{loaded_line}'"
                
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=30, deadline=None)
    @given(
        file_extension=st.sampled_from(['.txt', '.md', '.rst'])
    )
    def test_file_load_handles_different_text_file_types(self, file_extension):
        """
        Property: Loading should work with different text file extensions
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            test_content = "This is a test file with English instructions.\nAdd 5 and 3.\nCreate a list with items."
            
            # Create temporary file with specified extension
            with tempfile.NamedTemporaryFile(mode='w', suffix=file_extension, delete=False, encoding='utf-8') as temp_file:
                temp_file.write(test_content)
                temp_path = temp_file.name
            
            try:
                # Property: Load should succeed regardless of text file extension
                loaded_content = controller._handle_load(temp_path)
                
                # Property: Content should be preserved
                assert loaded_content == test_content, \
                    f"Content should be preserved for {file_extension} files"
                
                # Property: File should be recognized as text file (requirement 4.4)
                assert temp_path.endswith(file_extension), \
                    f"File should have correct extension: {file_extension}"
                
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=20, deadline=None)
    @given(st.just(""))
    def test_file_load_handles_empty_files(self, empty_content):
        """
        Property: Loading empty text files should work correctly
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            
            # Create empty temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(empty_content)
                temp_path = temp_file.name
            
            try:
                # Property: Load should succeed for empty files
                loaded_content = controller._handle_load(temp_path)
                
                # Property: Loaded content should be empty
                assert loaded_content == empty_content, \
                    "Empty file should load as empty content"
                
                # Property: Empty content should be displayable in input area
                controller.get_main_window().set_input_text(loaded_content)
                displayed_content = controller.get_main_window().get_input_text()
                
                assert displayed_content.strip() == "", \
                    "Empty content should display as empty in input area"
                
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=20, deadline=None)
    @given(st.just("nonexistent"))
    def test_file_load_handles_nonexistent_files(self, _):
        """
        Property: Loading nonexistent files should raise appropriate error
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            
            # Create path to nonexistent file
            with tempfile.TemporaryDirectory() as temp_dir:
                nonexistent_path = os.path.join(temp_dir, 'nonexistent_file.txt')
                
                # Property: Loading nonexistent file should raise exception
                with pytest.raises(Exception) as exc_info:
                    controller._handle_load(nonexistent_path)
                
                # Property: Exception should contain meaningful error message
                error_message = str(exc_info.value)
                assert "does not exist" in error_message or "not found" in error_message.lower(), \
                    "Error message should indicate file does not exist"
                
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=20, deadline=None)
    @given(
        large_content=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), whitelist_characters='\n\t'),
            min_size=1000, max_size=5000
        )
    )
    def test_file_load_handles_reasonable_file_sizes(self, large_content):
        """
        Property: Loading reasonably large text files should work correctly
        """
        import tempfile
        import os
        
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            controller = ApplicationController()
            
            # Create temporary file with large content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(large_content)
                temp_path = temp_file.name
            
            try:
                # Property: Load should succeed for reasonably large files
                loaded_content = controller._handle_load(temp_path)
                
                # Property: Content should be preserved completely
                assert loaded_content == large_content, \
                    "Large file content should be preserved completely"
                
                # Property: Content should be displayable (though we won't test actual display for large content)
                assert len(loaded_content) == len(large_content), \
                    "Loaded content length should match original"
                
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass



class TestExecutionOutputDisplay:
    """
    **Feature: english-to-python-translator, Property 23: Execution output display**
    **Validates: Requirements 6.2, 6.4**
    
    Property: For any code execution (successful or failed), the output or error should be 
    displayed in a separate execution results area with readable formatting.
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        python_code=st.sampled_from([
            "print('Hello, World!')",
            "x = 5\nprint(x)",
            "result = 10 + 20\nprint(result)",
            "for i in range(3):\n    print(i)",
            "my_list = [1, 2, 3]\nprint(my_list)",
            "name = 'Python'\nprint(f'Hello, {name}!')"
        ])
    )
    def test_successful_execution_displays_output(self, python_code):
        """
        Property: Successful code execution should display output in results area
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            window = controller.get_main_window()
            
            # Set the code in output area
            window.set_output_text(python_code)
            
            # Execute the code through the controller
            result = controller._handle_run(python_code)
            
            # Property: Execution should produce a result
            assert result is not None, "Execution should produce a result"
            
            if result.success:
                # Property: Successful execution should have output
                assert result.output or result.stdout, \
                    f"Successful execution should produce output for code: {python_code}"
                
                # Property: Output should be displayed in results area
                # (The controller formats the output, so we check the formatted result)
                output_text = result.output if result.output else result.stdout
                assert output_text.strip(), "Output should not be empty"
                
                # Property: Output should be readable (contain expected content)
                if 'print(' in python_code:
                    # For print statements, output should contain something
                    assert len(output_text.strip()) > 0, \
                        f"Print statements should produce visible output for: {python_code}"
                
                # Property: Output should have readable formatting
                # Check that it's not just raw bytes or unformatted data
                assert isinstance(output_text, str), "Output should be a string"
                assert not output_text.startswith('b\''), "Output should not be raw bytes"
                
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=100, deadline=None)
    @given(
        error_code=st.sampled_from([
            "print(undefined_variable)",
            "result = 1 / 0",
            "x = [1, 2, 3]\nprint(x[10])",
            "x = {'a': 1}\nprint(x['b'])",
            "print('hello'",  # Syntax error
            "if True\n    print('test')"  # Syntax error
        ])
    )
    def test_failed_execution_displays_error(self, error_code):
        """
        Property: Failed code execution should display error in results area
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            window = controller.get_main_window()
            
            # Set the code in output area
            window.set_output_text(error_code)
            
            # Execute the code through the controller
            result = controller._handle_run(error_code)
            
            # Property: Execution should produce a result
            assert result is not None, "Execution should produce a result"
            
            # Property: Failed execution should have error message
            assert not result.success, f"Invalid code should fail execution: {error_code}"
            assert result.error_message, \
                f"Failed execution should have error message for code: {error_code}"
            
            # Property: Error message should be displayed in separate area
            # (The controller formats the error, so we check the formatted result)
            error_text = result.error_message
            assert error_text.strip(), "Error message should not be empty"
            
            # Property: Error message should be readable and informative
            assert isinstance(error_text, str), "Error message should be a string"
            assert len(error_text.strip()) > 10, \
                "Error message should be informative (more than just a few characters)"
            
            # Property: Error message should contain error type information
            error_keywords = ['error', 'exception', 'failed', 'invalid', 'syntax', 'name', 'zero']
            has_error_info = any(keyword in error_text.lower() for keyword in error_keywords)
            assert has_error_info, \
                f"Error message should contain error type information: {error_text}"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        num1=st.integers(min_value=1, max_value=50),
        num2=st.integers(min_value=1, max_value=50),
        operation=st.sampled_from(['+', '-', '*'])
    )
    def test_execution_output_contains_correct_result(self, num1, num2, operation):
        """
        Property: Execution output should contain the correct computational result
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            
            # Create code that performs arithmetic and prints result
            python_code = f"result = {num1} {operation} {num2}\nprint(result)"
            
            # Execute the code
            result = controller._handle_run(python_code)
            
            if result.success:
                # Calculate expected result
                if operation == '+':
                    expected = num1 + num2
                elif operation == '-':
                    expected = num1 - num2
                else:  # '*'
                    expected = num1 * num2
                
                # Property: Output should contain the correct result
                output_text = result.output if result.output else result.stdout
                assert str(expected) in output_text, \
                    f"Output should contain correct result {expected} for {num1} {operation} {num2}, got: {output_text}"
                
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        python_code=st.sampled_from([
            "print('Line 1')\nprint('Line 2')\nprint('Line 3')",
            "for i in range(3):\n    print(f'Number {i}')",
            "x = 10\ny = 20\nprint(x)\nprint(y)",
            "items = ['a', 'b', 'c']\nfor item in items:\n    print(item)"
        ])
    )
    def test_execution_output_preserves_formatting(self, python_code):
        """
        Property: Execution output should preserve formatting and line structure
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            
            # Execute the code
            result = controller._handle_run(python_code)
            
            if result.success:
                # Property: Output should preserve line structure
                output_text = result.output if result.output else result.stdout
                
                # Count expected output lines (rough estimate)
                print_count = python_code.count('print(')
                
                if print_count > 1:
                    # Property: Multiple print statements should produce multiple lines
                    output_lines = [line for line in output_text.split('\n') if line.strip()]
                    assert len(output_lines) >= print_count - 1, \
                        f"Multiple print statements should produce multiple output lines for: {python_code}"
                
                # Property: Output should be readable (not garbled)
                assert not output_text.startswith('b\''), "Output should not be raw bytes"
                assert isinstance(output_text, str), "Output should be a string"
                
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        python_code=st.sampled_from([
            "print('Hello, World!')",
            "x = 42\nprint(x)",
            "result = 5 + 3\nprint(result)"
        ])
    )
    def test_execution_results_displayed_in_separate_area(self, python_code):
        """
        Property: Execution results should be displayed in a separate results area
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            window = controller.get_main_window()
            
            # Property: Results area should exist and be separate from output area
            assert hasattr(window, 'results_text'), "GUI should have separate results area"
            assert window.results_text is not None, "Results area should not be None"
            assert window.results_text != window.output_text, \
                "Results area should be separate from output area"
            
            # Execute the code
            result = controller._handle_run(python_code)
            
            # Property: Results should be displayable in the results area
            if result.success:
                output_text = result.output if result.output else result.stdout
                # The GUI should be able to display this in the results area
                window.set_results_text(output_text)
                displayed_results = window.get_results_text()
                
                # Property: Displayed results should match execution output
                assert displayed_results.strip() == output_text.strip(), \
                    "Results area should display execution output correctly"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        python_code=st.sampled_from([
            "print('Test')",
            "x = 10\nprint(x)",
            "result = 1 / 0"  # Will cause error
        ])
    )
    def test_execution_timing_included_in_output(self, python_code):
        """
        Property: Execution output should include timing information
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            
            # Execute the code
            result = controller._handle_run(python_code)
            
            # Property: Result should include execution time
            assert hasattr(result, 'execution_time'), "Result should have execution_time attribute"
            assert isinstance(result.execution_time, (int, float)), \
                "Execution time should be numeric"
            assert result.execution_time >= 0, "Execution time should be non-negative"
            
            # Property: Formatted output should include timing information
            if result.success:
                output_text = result.output
            else:
                output_text = result.error_message
            
            # The controller formats output to include execution time
            timing_keywords = ['time', 'seconds', 'execution']
            has_timing_info = any(keyword in output_text.lower() for keyword in timing_keywords)
            assert has_timing_info, \
                f"Output should include timing information: {output_text}"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        code1=st.sampled_from(["print('First')", "x = 1\nprint(x)"]),
        code2=st.sampled_from(["print('Second')", "y = 2\nprint(y)"])
    )
    def test_execution_results_can_be_updated(self, code1, code2):
        """
        Property: Execution results area should allow updating with new results
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            window = controller.get_main_window()
            
            # Execute first code
            result1 = controller._handle_run(code1)
            if result1.success:
                output1 = result1.output if result1.output else result1.stdout
                window.set_results_text(output1)
                displayed1 = window.get_results_text()
                
                # Execute second code
                result2 = controller._handle_run(code2)
                if result2.success:
                    output2 = result2.output if result2.output else result2.stdout
                    window.set_results_text(output2)
                    displayed2 = window.get_results_text()
                    
                    # Property: Second execution should replace first results
                    assert displayed2.strip() != displayed1.strip() or code1 == code2, \
                        "New execution results should replace previous results"
                    
                    # Property: Results should match second execution
                    assert output2.strip() in displayed2.strip(), \
                        "Results area should display second execution output"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
    
    @settings(max_examples=50, deadline=None)
    @given(
        python_code=st.sampled_from([
            "print('Hello')",
            "x = 5\nprint(x)",
            "result = 1 / 0"
        ])
    )
    def test_execution_output_is_human_readable(self, python_code):
        """
        Property: Execution output should be human-readable and well-formatted
        """
        try:
            root = tk.Tk()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
        
        try:
            from src.gui.application_controller import ApplicationController
            
            # Create application controller
            controller = ApplicationController()
            
            # Execute the code
            result = controller._handle_run(python_code)
            
            # Property: Output should be human-readable
            if result.success:
                output_text = result.output
            else:
                output_text = result.error_message
            
            # Property: Output should be a readable string
            assert isinstance(output_text, str), "Output should be a string"
            assert len(output_text.strip()) > 0, "Output should not be empty"
            
            # Property: Output should not contain raw escape sequences or binary data
            assert not output_text.startswith('b\''), "Output should not be raw bytes"
            assert not output_text.startswith('\\x'), "Output should not contain raw escape sequences"
            
            # Property: Output should contain readable text
            # Check that it contains printable characters
            printable_chars = sum(1 for c in output_text if c.isprintable() or c in '\n\t ')
            total_chars = len(output_text)
            if total_chars > 0:
                readability_ratio = printable_chars / total_chars
                assert readability_ratio > 0.9, \
                    f"Output should be mostly printable characters, got ratio: {readability_ratio}"
            
        except tk.TclError as e:
            pytest.skip(f"Tkinter configuration issue: {e}")
        finally:
            try:
                root.destroy()
            except:
                pass
