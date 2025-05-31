#!/usr/bin/env python3
"""RadioForms application entry point.

This module serves as the main entry point for the RadioForms application.
It sets up the application environment, handles command-line arguments,
and initializes the GUI application.

Usage:
    python -m src.main
    
Example:
    # Start the application
    python -m src.main
    
    # Start with debug logging
    python -m src.main --debug
    
    # Show version information
    python -m src.main --version
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import NoReturn, Optional

# Application metadata
__version__ = "0.1.0"
__author__ = "RadioForms Development Team"
__description__ = "ICS Forms Management Application for Emergency Response"


def setup_logging(level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        
    Example:
        setup_logging("DEBUG", Path("radioforms.log"))
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            logging.info(f"Logging to file: {log_file}")
        except OSError as e:
            logging.warning(f"Could not set up file logging: {e}")
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logging.info(f"Logging configured at {level.upper()} level")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed command-line arguments
        
    Example:
        args = parse_arguments()
        if args.debug:
            setup_logging("DEBUG")
    """
    parser = argparse.ArgumentParser(
        prog="radioforms",
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Start the application
  %(prog)s --debug            Start with debug logging
  %(prog)s --version          Show version information
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path (default: no file logging)"
    )
    
    parser.add_argument(
        "--database",
        type=Path,
        help="Database file path (default: radioforms.db)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no GUI, for testing and automation)"
    )
    
    return parser.parse_args()


def check_requirements() -> bool:
    """Check if all required dependencies are available.
    
    Returns:
        True if all requirements are met, False otherwise
        
    This function performs a basic environment check before starting
    the GUI application.
    """
    logger = logging.getLogger(__name__)
    
    # Check Python version
    if sys.version_info < (3, 10):
        logger.error(
            f"Python 3.10+ required, got {sys.version_info[0]}.{sys.version_info[1]}"
        )
        return False
    
    logger.info(f"Python version: {sys.version}")
    
    # Check for PySide6
    try:
        import PySide6
        logger.info(f"PySide6 version: {PySide6.__version__}")
    except ImportError:
        logger.error("PySide6 not found. Please install with: pip install PySide6")
        return False
    
    # Check for required directories
    app_dir = Path(__file__).parent
    required_dirs = ["models", "ui", "database", "services"]
    
    for dir_name in required_dirs:
        dir_path = app_dir / dir_name
        if not dir_path.exists():
            logger.warning(f"Directory not found: {dir_path}")
    
    logger.info("Requirements check completed successfully")
    return True


def main() -> NoReturn:
    """Main application entry point.
    
    This function:
    1. Parses command-line arguments
    2. Sets up logging
    3. Checks requirements
    4. Initializes and starts the GUI application
    
    Raises:
        SystemExit: Always exits with appropriate code
    """
    # Parse arguments first (for --version, --help)
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level, args.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting RadioForms v{__version__}")
    logger.info(f"Python {sys.version}")
    logger.info(f"Command line arguments: {args}")
    
    try:
        # Check if running in headless mode
        if args.headless:
            logger.info("Running in headless mode")
            from .app.headless_app import HeadlessApplication
            
            app = HeadlessApplication(
                database_path=args.database,
                debug=args.debug
            )
            
            logger.info("Starting headless application")
            exit_code = app.run()
            
            logger.info(f"Headless application finished with exit code: {exit_code}")
            sys.exit(exit_code)
        
        # Check requirements for GUI mode
        if not check_requirements():
            logger.error("Requirements check failed")
            sys.exit(1)
        
        # Import GUI components after requirements check
        from .app.application import Application
        
        # Create and run application
        logger.info("Initializing GUI application")
        app = Application(
            database_path=args.database,
            debug=args.debug
        )
        
        logger.info("Starting application main loop")
        exit_code = app.run()
        
        logger.info(f"Application finished with exit code: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()