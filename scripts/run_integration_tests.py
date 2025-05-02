#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run Integration Tests Script.

This script runs the functional integration tests to verify that all improvements
have been properly integrated into the main codebase.
"""

import os
import sys
import unittest
import logging
from pathlib import Path

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_tests():
    """Run the integration tests."""
    logger.info("Running RadioForms Integration Tests")
    
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(test_loader.loadTestsFromName("radioforms.tests.test_functional_integration"))
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Log results
    logger.info(f"Tests Run: {result.testsRun}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    
    # Print detailed errors
    if result.errors:
        logger.error("Test Errors:")
        for test, error in result.errors:
            logger.error(f"{test}: {error}")
    
    # Print detailed failures
    if result.failures:
        logger.error("Test Failures:")
        for test, failure in result.failures:
            logger.error(f"{test}: {failure}")
    
    return len(result.errors) == 0 and len(result.failures) == 0


def verify_implementations():
    """Verify that all implementations have been integrated correctly."""
    logger.info("Verifying implementations")
    
    # Check that enhanced form resolver is imported in form_model_registry
    try:
        from radioforms.models.form_model_registry import resolve_form_type
        logger.info("✅ Enhanced form resolver is integrated into form_model_registry")
    except ImportError:
        logger.error("❌ Enhanced form resolver not integrated into form_model_registry")
        return False
    
    # Check that SchemaManager is imported in db_manager
    try:
        from radioforms.database.db_manager import DBManager
        from radioforms.database.schema_manager import SchemaManager
        
        # Create test manager
        db_path = os.path.join(os.path.dirname(__file__), "test_integration.db")
        db_manager = DBManager(db_path)
        
        # Verify that verify_schema method exists
        if hasattr(db_manager, "verify_schema"):
            logger.info("✅ Schema manager is integrated into db_manager")
        else:
            logger.error("❌ Schema manager method verify_schema not found in db_manager")
            return False
        
        # Clean up test database
        if os.path.exists(db_path):
            os.unlink(db_path)
            
    except (ImportError, AttributeError) as e:
        logger.error(f"❌ Schema manager integration check failed: {e}")
        return False
    
    # Check that test fixtures are available
    try:
        from radioforms.tests.fixtures.db_fixture import DatabaseFixtureContext
        logger.info("✅ Database fixtures are available")
    except ImportError:
        logger.error("❌ Database fixtures not found")
        return False
    
    # Check that functional test utilities are available
    try:
        from radioforms.tests.test_utils.functional_test_utils import FunctionalTestCase
        logger.info("✅ Functional test utilities are available")
    except ImportError:
        logger.error("❌ Functional test utilities not found")
        return False
    
    return True


if __name__ == "__main__":
    # Verify implementations
    implementations_ok = verify_implementations()
    
    if not implementations_ok:
        logger.error("Implementation verification failed")
        sys.exit(1)
    
    # Run tests
    tests_ok = run_tests()
    
    if not tests_ok:
        logger.error("Integration tests failed")
        sys.exit(1)
    
    logger.info("All verification and tests passed successfully")
    sys.exit(0)
