#!/usr/bin/env python3
"""
English to Python Translator
Main application entry point

This module provides the main entry point for the English to Python Translator application.
It initializes all components, sets up the GUI, and starts the main event loop with proper
error handling for application startup.
"""

import sys
import os
import logging
import traceback
from typing import Optional

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def setup_logging() -> None:
    """
    Setup logging configuration for the application
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(current_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Configure logging
        log_file = os.path.join(logs_dir, 'translator.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Log startup
        logger = logging.getLogger(__name__)
        logger.info("English to Python Translator starting up...")
        
    except Exception as e:
        # If logging setup fails, continue without logging
        print(f"Warning: Could not setup logging: {e}")


def check_dependencies() -> bool:
    """
    Check if all required dependencies are available
    
    Returns:
        True if all dependencies are available, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Check for required modules
        required_modules = [
            ('tkinter', 'GUI framework'),
            ('nltk', 'Natural language processing'),
            ('ast', 'Python AST parsing'),
            ('re', 'Regular expressions'),
            ('json', 'JSON handling'),
        ]
        
        missing_modules = []
        
        for module_name, description in required_modules:
            try:
                __import__(module_name)
                logger.info(f"✓ {module_name} ({description}) - Available")
            except ImportError:
                missing_modules.append((module_name, description))
                logger.error(f"✗ {module_name} ({description}) - Missing")
        
        if missing_modules:
            print("\nMissing required dependencies:")
            for module_name, description in missing_modules:
                print(f"  - {module_name}: {description}")
            print("\nPlease install missing dependencies and try again.")
            return False
        
        logger.info("All required dependencies are available")
        return True
        
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        return False


def initialize_application() -> Optional['ApplicationController']:
    """
    Initialize all application components
    
    Returns:
        ApplicationController instance if successful, None otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing application components...")
        
        # Import application controller
        from gui.application_controller import ApplicationController
        
        # Create application controller (this initializes all components)
        logger.info("Creating application controller...")
        app = ApplicationController()
        
        # Verify all components are initialized
        app_info = app.get_application_info()
        logger.info(f"Application info: {app_info}")
        
        if not app_info.get('translation_engine_ready', False):
            raise RuntimeError("Translation engine failed to initialize")
        
        if not app_info.get('execution_service_ready', False):
            raise RuntimeError("Code execution service failed to initialize")
        
        if not app_info.get('gui_ready', False):
            raise RuntimeError("GUI interface failed to initialize")
        
        logger.info("All application components initialized successfully")
        print("Application structure initialized successfully!")
        return app
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        print(f"Import error: {e}")
        print("Please ensure all source files are present and accessible.")
        return None
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Initialization error: {e}")
        return None


def main() -> int:
    """
    Main application entry point
    
    Initializes all components, sets up GUI, and starts the main event loop
    with proper error handling for application startup.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== English to Python Translator Starting ===")
        
        # Check system requirements
        logger.info("Checking system requirements...")
        if not check_dependencies():
            logger.error("Dependency check failed")
            return 1
        
        # Initialize application components
        logger.info("Initializing application...")
        app = initialize_application()
        
        if app is None:
            logger.error("Application initialization failed")
            return 1
        
        # Check if running in test mode (no GUI)
        if '--test' in sys.argv or os.environ.get('PYTEST_CURRENT_TEST'):
            logger.info("Running in test mode - skipping GUI startup")
            logger.info("Application shutdown completed successfully")
            return 0
        
        # Start the application
        logger.info("Starting GUI application...")
        app.run()
        
        logger.info("Application shutdown completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        print("\nApplication interrupted by user")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected application error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Fatal error: {e}")
        print("Check the log file for detailed error information.")
        return 1
    
    finally:
        logger.info("=== English to Python Translator Shutdown ===")


if __name__ == "__main__":
    # Set exit code based on main() return value
    exit_code = main()
    sys.exit(exit_code)