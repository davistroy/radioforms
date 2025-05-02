#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Test Runner for RadioForms.

This module provides a test runner that executes all tests for the enhanced
RadioForms components. It can be used to verify the functionality of the
newly implemented features.
"""

import sys
import unittest
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def discover_and_run_tests():
    """
    Discover and run all enhanced tests.
    
    Returns:
        True if all tests pass, False otherwise
    """
    logger.info("Starting RadioForms enhanced test suite...")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add specific test modules for the enhanced components
    test_modules = [
        'test_config_manager',
        'test_db_manager',
        'test_form_model_registry',
        'test_enhanced_form_tab_widget',
        'test_enhanced_implementation',
        'test_enhanced_form_integration',
        'test_enhanced_ics214_form',
        'test_startup_wizard'
    ]
    
    # Add tests from each module
    for module_name in test_modules:
        try:
            # Import the module
            module = __import__(f'radioforms.tests.{module_name}', fromlist=['*'])
            
            # Find all test classes in the module
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj is not unittest.TestCase:
                    # Skip tests that require manual interaction
                    if hasattr(obj, '__unittest_skip__') and obj.__unittest_skip__:
                        logger.info(f"Skipping {obj.__name__}: {obj.__unittest_skip_why__}")
                        continue
                        
                    # Add test class to suite
                    suite.addTest(unittest.makeSuite(obj))
                    
            logger.info(f"Added tests from {module_name}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not import tests from {module_name}: {e}")
    
    # Run the tests
    logger.info("Running tests...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    logger.info(f"Tests Run: {result.testsRun}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    
    if result.errors or result.failures:
        logger.error("Some tests failed!")
        return False
    else:
        logger.info("All tests passed!")
        return True


def run_ui_tests():
    """
    Run UI-specific tests.
    
    The UI tests are separated because they require a QApplication instance
    and may involve user interaction or display of widgets.
    
    Returns:
        True if all tests pass, False otherwise
    """
    logger.info("Starting RadioForms UI test suite...")
    
    # Import here to avoid early creation of QApplication
    from PySide6.QtWidgets import QApplication
    
    # Create QApplication instance if needed
    app = QApplication.instance() or QApplication([])
    
    # Create test suite for UI tests
    suite = unittest.TestSuite()
    
    # Add UI test modules (these are marked as skip by default, we'll unskip them)
    ui_test_modules = [
        'test_enhanced_form_tab_widget',
        'test_startup_wizard',
    ]
    
    for module_name in ui_test_modules:
        try:
            # Import the module
            module = __import__(f'radioforms.tests.{module_name}', fromlist=['*'])
            
            # Find all UI test classes in the module
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and hasattr(obj, '__unittest_skip__'):
                    # Create a new class that doesn't have the skip attribute
                    new_class = type(obj.__name__, (obj,), {})
                    new_class.__unittest_skip__ = False
                    
                    # Add test class to suite
                    suite.addTest(unittest.makeSuite(new_class))
                    
            logger.info(f"Added UI tests from {module_name}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not import UI tests from {module_name}: {e}")
    
    # Run the tests
    logger.info("Running UI tests...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    logger.info(f"UI Tests Run: {result.testsRun}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    
    if result.errors or result.failures:
        logger.error("Some UI tests failed!")
        return False
    else:
        logger.info("All UI tests passed!")
        return True


def main():
    """
    Main entry point for the test runner.
    
    Returns:
        0 if all tests pass, 1 otherwise
    """
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run RadioForms enhanced tests")
    parser.add_argument("--ui", action="store_true", help="Run UI tests (may require user interaction)")
    parser.add_argument("--all", action="store_true", help="Run all tests including UI tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Set log level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests based on arguments
    success = True
    
    if args.ui or args.all:
        ui_success = run_ui_tests()
        success = success and ui_success
    
    if not args.ui or args.all:
        non_ui_success = discover_and_run_tests()
        success = success and non_ui_success
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
