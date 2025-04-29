#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the configuration and startup components.

This module contains tests for the configuration manager, system integrity
checker, and startup wizard components.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch
from datetime import datetime
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from radioforms.database.db_manager import DatabaseManager
from radioforms.config.config_manager import ConfigManager, SystemIntegrityChecker
from radioforms.views.startup_wizard import (
    StartupWizard, WelcomePage, UserProfilePage, 
    IncidentPage, DiagnosticsPage, CompletionPage
)


class ConfigManagerTestCase(unittest.TestCase):
    """Test cases for the ConfigManager class."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary database for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create the config manager
        self.config_manager = ConfigManager(self.db_manager)
        
    def tearDown(self):
        """Clean up after the test case."""
        # Close the database connection
        self.db_manager.close()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_init_config(self):
        """Test that the config manager initializes default settings."""
        # The constructor should have already called _init_config
        
        # Verify that first_run setting is set to "false"
        first_run = self.config_manager.get_setting(ConfigManager.FIRST_RUN)
        self.assertEqual(first_run, "false")
        
        # Verify that app_version is set
        app_version = self.config_manager.get_setting(ConfigManager.APP_VERSION)
        self.assertIsNotNone(app_version)
    
    def test_is_first_run(self):
        """Test the is_first_run method."""
        # By default, should be false after initialization
        self.assertFalse(self.config_manager.is_first_run())
        
        # Set it to true
        self.config_manager.set_setting(ConfigManager.FIRST_RUN, "true")
        self.assertTrue(self.config_manager.is_first_run())
        
        # Set it to false again
        self.config_manager.set_setting(ConfigManager.FIRST_RUN, "false")
        self.assertFalse(self.config_manager.is_first_run())
    
    def test_get_setting(self):
        """Test getting settings."""
        # Test with a non-existent setting
        value = self.config_manager.get_setting("non_existent")
        self.assertIsNone(value)
        
        # Test with a non-existent setting and default value
        value = self.config_manager.get_setting("non_existent", "default")
        self.assertEqual(value, "default")
        
        # Test with an existing setting
        self.config_manager.set_setting("test_key", "test_value")
        value = self.config_manager.get_setting("test_key")
        self.assertEqual(value, "test_value")
    
    def test_set_setting(self):
        """Test setting settings."""
        # Set a new setting
        result = self.config_manager.set_setting("test_key", "test_value")
        self.assertTrue(result)
        
        # Get the setting to verify
        value = self.config_manager.get_setting("test_key")
        self.assertEqual(value, "test_value")
        
        # Update an existing setting
        result = self.config_manager.set_setting("test_key", "new_value")
        self.assertTrue(result)
        
        # Get the setting to verify
        value = self.config_manager.get_setting("test_key")
        self.assertEqual(value, "new_value")
    
    def test_clear_cache(self):
        """Test clearing the settings cache."""
        # Set a setting
        self.config_manager.set_setting("test_key", "test_value")
        
        # Get the setting to populate the cache
        self.config_manager.get_setting("test_key")
        
        # Directly modify the setting in the database
        self.db_manager.execute(
            "UPDATE settings SET value = ? WHERE key = ?",
            ("modified_value", "test_key")
        )
        self.db_manager.commit()
        
        # Get the setting again, should still return cached value
        value = self.config_manager.get_setting("test_key")
        self.assertEqual(value, "test_value")
        
        # Clear the cache
        self.config_manager.clear_cache()
        
        # Get the setting again, should return the modified value
        value = self.config_manager.get_setting("test_key")
        self.assertEqual(value, "modified_value")
    
    def test_user_management(self):
        """Test user profile management."""
        # No current user initially
        current_user = self.config_manager.get_current_user()
        self.assertIsNone(current_user)
        
        # Create a user
        user_data = {
            "name": "Test User",
            "call_sign": "N0CALL"
        }
        user_id = self.config_manager.create_or_update_user(user_data)
        self.assertIsNotNone(user_id)
        
        # Set as current user
        result = self.config_manager.set_current_user(user_id)
        self.assertTrue(result)
        
        # Get current user
        current_user = self.config_manager.get_current_user()
        self.assertIsNotNone(current_user)
        self.assertEqual(current_user["name"], "Test User")
        self.assertEqual(current_user["call_sign"], "N0CALL")
        
        # Get all users
        users = self.config_manager.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["name"], "Test User")
    
    def test_validate_database(self):
        """Test database validation."""
        # Should succeed with a valid database
        success, errors = self.config_manager.validate_database()
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)


class SystemIntegrityCheckerTestCase(unittest.TestCase):
    """Test cases for the SystemIntegrityChecker class."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a temporary database
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create the system integrity checker
        self.checker = SystemIntegrityChecker(self.db_manager, self.temp_dir)
    
    def tearDown(self):
        """Clean up after the test case."""
        # Close the database connection
        self.db_manager.close()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_check_file_system_access(self):
        """Test checking file system access."""
        # Should succeed with a valid directory
        success, errors = self.checker.check_file_system_access()
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
        
        # Test with a non-existent directory
        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        checker = SystemIntegrityChecker(self.db_manager, non_existent_dir)
        success, errors = checker.check_file_system_access()
        self.assertFalse(success)
        self.assertEqual(len(errors), 1)
    
    def test_check_database_connection(self):
        """Test checking database connection."""
        # Should succeed with a valid database
        success, errors = self.checker.check_database_connection()
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
    
    def test_check_all(self):
        """Test running all checks."""
        # Patch the disk space check to avoid platform-specific issues
        with patch.object(SystemIntegrityChecker, 'check_disk_space', 
                          return_value=(True, [])):
            # Should succeed with all valid checks
            success, results = self.checker.check_all()
            self.assertTrue(success)
            self.assertIn('file_system', results)
            self.assertIn('database', results)
            self.assertIn('disk_space', results)
            self.assertTrue(results['file_system']['success'])
            self.assertTrue(results['database']['success'])
            self.assertTrue(results['disk_space']['success'])


# Make sure QApplication exists for the tests
@pytest.fixture(scope="module")
def app():
    """Create a QApplication instance for the tests."""
    return QApplication.instance() or QApplication(sys.argv)


@pytest.mark.usefixtures("app")
class StartupWizardTestCase(unittest.TestCase):
    """Test cases for the StartupWizard class."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary database for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create configuration manager
        self.config_manager = ConfigManager(self.db_manager)
        
        # Mock the config manager in the wizard
        self.wizard_patcher = patch('radioforms.views.startup_wizard.ConfigManager')
        self.mock_config_manager = self.wizard_patcher.start()
        self.mock_config_manager.return_value = self.config_manager
        
        # Create the wizard
        self.wizard = StartupWizard(self.db_manager, self.temp_dir)
    
    def tearDown(self):
        """Clean up after the test case."""
        # Stop the patcher
        self.wizard_patcher.stop()
        
        # Close the database connection
        self.db_manager.close()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_wizard_initialization(self):
        """Test that the wizard initializes correctly."""
        # Verify that the wizard has the correct number of pages
        self.assertEqual(self.wizard.pageIds(), list(range(5)))
        
        # Verify the page types
        self.assertIsInstance(self.wizard.page(0), WelcomePage)
        self.assertIsInstance(self.wizard.page(1), UserProfilePage)
        self.assertIsInstance(self.wizard.page(2), IncidentPage)
        self.assertIsInstance(self.wizard.page(3), DiagnosticsPage)
        self.assertIsInstance(self.wizard.page(4), CompletionPage)


if __name__ == '__main__':
    unittest.main()
