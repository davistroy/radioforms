#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the startup wizard component.

This module contains tests for the StartupWizard class and related pages.
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
from radioforms.config.config_manager import ConfigManager
from radioforms.views.startup_wizard import (
    StartupWizard, WelcomePage, UserProfilePage, 
    IncidentPage, DiagnosticsPage, CompletionPage
)


# Make sure QApplication exists for the tests
@pytest.fixture(scope="module")
def app():
    """Create a QApplication instance for the tests."""
    return QApplication.instance() or QApplication(sys.argv)


@pytest.mark.usefixtures("app")
class StartupWizardTestCase(unittest.TestCase):
    """Test case for the startup wizard."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary database for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db_manager = DatabaseManager(self.db_path)
        
        # Mock the configuration manager
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        self.mock_config_manager.get_users.return_value = []
        self.mock_config_manager.get_setting.return_value = None
        self.mock_config_manager.is_first_run.return_value = True
        
        # Mock the system checker
        self.mock_checker = MagicMock()
        self.mock_checker.check_all.return_value = (True, {})
        
        # Patch the ConfigManager constructor to return our mock
        self.config_patcher = patch('radioforms.views.startup_wizard.ConfigManager', 
                                   return_value=self.mock_config_manager)
        self.mock_config_class = self.config_patcher.start()
        
        # Patch the SystemIntegrityChecker
        self.checker_patcher = patch('radioforms.views.startup_wizard.SystemIntegrityChecker',
                                    return_value=self.mock_checker)
        self.mock_checker_class = self.checker_patcher.start()
        
        # Mock the IncidentDAO
        self.mock_incident_dao = MagicMock()
        self.mock_incident_dao.get_all.return_value = []
        self.incident_dao_patcher = patch('radioforms.views.startup_wizard.IncidentDAO',
                                         return_value=self.mock_incident_dao)
        self.mock_incident_dao_class = self.incident_dao_patcher.start()
        
        # Create the wizard
        self.wizard = StartupWizard(self.db_manager, self.temp_dir)
    
    def tearDown(self):
        """Clean up after the test case."""
        # Stop the patchers
        self.config_patcher.stop()
        self.checker_patcher.stop()
        self.incident_dao_patcher.stop()
        
        # Close the database connection
        self.db_manager.close()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test that the wizard initializes correctly."""
        # Verify that the wizard has the correct number of pages
        self.assertEqual(len(self.wizard.pageIds()), 5)
        
        # Verify the page types
        self.assertIsInstance(self.wizard.page(0), WelcomePage)
        self.assertIsInstance(self.wizard.page(1), UserProfilePage)
        self.assertIsInstance(self.wizard.page(2), IncidentPage)
        self.assertIsInstance(self.wizard.page(3), DiagnosticsPage)
        self.assertIsInstance(self.wizard.page(4), CompletionPage)
        
        # Verify that the wizard has the correct title
        self.assertEqual(self.wizard.windowTitle(), "RadioForms Setup")
    
    def test_welcome_page(self):
        """Test that the welcome page displays correctly."""
        welcome_page = self.wizard.page(0)
        self.assertEqual(welcome_page.title(), "Welcome to RadioForms")
        self.assertIn("This wizard will help you", welcome_page.subTitle())
    
    def test_user_profile_page(self):
        """Test that the user profile page displays correctly."""
        user_page = self.wizard.page(1)
        self.assertEqual(user_page.title(), "User Profile")
        self.assertIn("Please provide your information", user_page.subTitle())
    
    def test_incident_page(self):
        """Test that the incident page displays correctly."""
        incident_page = self.wizard.page(2)
        self.assertEqual(incident_page.title(), "Incident Information")
        self.assertIn("Please provide information about the incident", incident_page.subTitle())
    
    def test_diagnostics_page(self):
        """Test that the diagnostics page displays correctly."""
        diagnostics_page = self.wizard.page(3)
        self.assertEqual(diagnostics_page.title(), "System Diagnostics")
        self.assertIn("Checking system requirements", diagnostics_page.subTitle())
    
    def test_completion_page(self):
        """Test that the completion page displays correctly."""
        completion_page = self.wizard.page(4)
        self.assertEqual(completion_page.title(), "Setup Complete")
        self.assertIn("The application is now ready", completion_page.subTitle())
    
    def test_wizard_accepts(self):
        """Test that the wizard updates the configuration on accept."""
        # Set up the mock
        self.mock_config_manager.set_setting.return_value = True
        
        # Patch the FIRST_RUN constant in the startup_wizard module
        with patch('radioforms.views.startup_wizard.ConfigManager.FIRST_RUN', "app.first_run"):
            # Call accept
            self.wizard.accept()
            
            # Check that the first run setting was updated
            self.mock_config_manager.set_setting.assert_called_with(
                "app.first_run", "false"
            )


if __name__ == '__main__':
    unittest.main()
