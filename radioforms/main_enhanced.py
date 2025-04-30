#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced main entry point for RadioForms application.

This script provides the main entry point for the RadioForms application,
using the enhanced components that have been developed.
"""

import sys
import os
import logging
from pathlib import Path
import argparse

from PySide6.QtWidgets import QApplication

from radioforms.controllers.app_controller_enhanced import run_application


def setup_logging(verbose: bool = False):
    """
    Set up logging for the application.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path.home() / ".radioforms" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up log file path
    log_file = logs_dir / "radioforms.log"
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("RadioForms starting up...")
    logger.info(f"Logging to {log_file}")
    
    return logger


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="RadioForms - Digital ICS Form Manager")
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset configuration and run initial setup wizard"
    )
    
    parser.add_argument(
        "--test-wizard",
        action="store_true",
        help="Run the startup wizard in test mode"
    )
    
    return parser.parse_args()


def reset_configuration():
    """Reset application configuration."""
    # Get config file path
    config_path = Path.home() / ".radioforms" / "config.ini"
    
    # Delete configuration file if it exists
    if config_path.exists():
        config_path.unlink()
        
    # Log action
    logging.info("Configuration reset. Startup wizard will run on next launch.")


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    logger = setup_logging(args.verbose)
    
    # Reset configuration if requested
    if args.reset_config:
        reset_configuration()
        
    # Run the startup wizard test if requested
    if args.test_wizard:
        from radioforms.tests.test_startup_wizard import main as test_wizard
        return test_wizard()
        
    # Run the application
    logger.info("Starting RadioForms application")
    return run_application()


if __name__ == "__main__":
    sys.exit(main())
