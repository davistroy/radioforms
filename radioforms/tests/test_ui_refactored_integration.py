#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI integration tests for the refactored controllers.

This module tests the integration between UI components and the refactored
controller implementations to verify that the UI can correctly interact with
the refactored DAO methods through the controller layer.
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from radioforms.database.db_manager import DatabaseManager
from radioforms.controllers.app_controller import AppController
from radioforms.controllers.api_controller import APIController
from radioforms.views.main_window import MainWindow, FormSelectionDialog
from radioforms.database.models.form import FormStatus
from radioforms.database.models.incident import Incident
from radioforms.database.models.user import User


# Create a QApplication instance for the tests
app = QApplication.instance() or QApplication(sys.argv)


class UIRefactoredIntegrationTests(unittest.TestCase):
    """
    Tests for verifying UI integration with refactored controllers.
    
    These tests create instances of UI components and controllers with test data
    to verify that the UI can correctly interact with the refactored controller
    implementations.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary database file
        fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Set up test database schema
        self._create_test_schema()
        
        # Create test data
        self._create_test_data()
        
        # Create the app controller with a mock config
        self._setup_app_controller()
        
        # Create test view
        self.main_window = MainWindow(self.app_controller)
    
    def tearDown(self):
        """Clean up resources."""
        if hasattr(self, 'db_manager') and self.db_manager:
            self.db_manager.close()
        
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
            
        # Close and delete the main window
        if hasattr(self, 'main_window'):
            self.main_window.close()
            self.main_window.deleteLater()
    
    def _create_test_schema(self):
        """Create test database schema."""
        # Create incidents table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create forms table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            form_type TEXT NOT NULL,
            title TEXT NOT NULL,
            creator_id INTEGER,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
        )
        ''')
        
        # Create form_versions table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS form_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            content TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES forms(id)
        )
        ''')
        
        # Create settings table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create users table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            call_sign TEXT UNIQUE,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    
    def _create_test_data(self):
        """Create test data in the database."""
        # Create test incidents
        for i in range(1, 4):
            self.db_manager.execute(
                "INSERT INTO incidents (name, description) VALUES (?, ?)",
                (f"Test Incident {i}", f"Description for incident {i}")
            )
        
        # Create test forms
        form_types = ["ICS-213", "ICS-214"]
        for incident_id in range(1, 4):
            for form_type in form_types:
                # Create a form
                form_id = self.db_manager.execute(
                    """
                    INSERT INTO forms (
                        incident_id, form_type, title, status
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        incident_id,
                        form_type,
                        f"{form_type} for Incident {incident_id}",
                        "draft"
                    )
                ).lastrowid
                
                # Create a form version
                content = {
                    "title": f"{form_type} for Incident {incident_id}",
                    "data": {
                        "field1": "Test value 1",
                        "field2": "Test value 2"
                    }
                }
                
                self.db_manager.execute(
                    """
                    INSERT INTO form_versions (
                        form_id, version_number, content
                    ) VALUES (?, ?, ?)
                    """,
                    (form_id, 1, str(content))
                )
        
        # Create test settings
        self.db_manager.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("app.first_run", "false")
        )
        
        # Create test users
        self.db_manager.execute(
            "INSERT INTO users (name, call_sign) VALUES (?, ?)",
            ("Test User", "TEST1")
        )
        
        # Commit changes
        self.db_manager.commit()
    
    def _setup_app_controller(self):
        """Set up the application controller with mocks."""
        # Create the API controller
        self.api_controller = APIController(self.db_manager)
        
        # Create a mock config for the app controller
        mock_config = MagicMock()
        mock_config.get.return_value = self.db_path
        
        # Create the app controller with mock config
        self.app_controller = AppController(None)
        self.app_controller.config = mock_config
        self.app_controller.db_manager = self.db_manager
        self.app_controller.api_controller = self.api_controller
        
        # Mock the config manager to avoid startup wizard
        mock_config_manager = MagicMock()
        mock_config_manager.is_first_run.return_value = False
        self.app_controller.config_manager = mock_config_manager
    
    def test_active_incidents_display(self):
        """Test that active incidents are correctly retrieved and displayed."""
        active_incidents = self.app_controller.get_active_incidents()
        
        # Assert correct number of incidents from our test data
        self.assertEqual(len(active_incidents), 3)
        
        # Assert data is retrieved correctly
        for i, incident in enumerate(active_incidents, 1):
            self.assertEqual(incident['id'], i)
            self.assertEqual(incident['name'], f"Test Incident {i}")
    
    def test_incident_stats(self):
        """Test that incident statistics are correctly calculated."""
        stats = self.app_controller.get_incident_stats()
        
        # Assert correct stats
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['active'], 3)
        self.assertEqual(stats['closed'], 0)
        
        # Close an incident
        self.api_controller.close_incident(1)
        
        # Check updated stats
        stats = self.app_controller.get_incident_stats()
        self.assertEqual(stats['active'], 2)
        self.assertEqual(stats['closed'], 1)
    
    def test_recent_forms(self):
        """Test that recent forms are correctly retrieved."""
        recent_forms = self.app_controller.get_recent_forms(limit=5)
        
        # Assert correct number of forms
        self.assertEqual(len(recent_forms), 5)
    
    def test_form_content(self):
        """Test that form content is correctly retrieved."""
        # Get a test form with content
        form_data = self.app_controller.get_form_with_content(1)
        
        # Assert form data is retrieved correctly
        self.assertIsNotNone(form_data)
        self.assertIn('form', form_data)
        self.assertIn('content', form_data)
        
        # Check form data
        form = form_data['form']
        self.assertEqual(form['id'], 1)
        self.assertEqual(form['incident_id'], 1)
        
        # Check content - this might need adjustment based on actual content format
        content = form_data['content']
        self.assertIsNotNone(content)
    
    @patch('radioforms.controllers.forms_controller.FormFactory')
    @patch('radioforms.controllers.forms_controller.FormManager')
    def test_form_creation_dialog(self, mock_form_manager, mock_form_factory):
        """Test form creation dialog interaction with controller."""
        # Setup mocks
        mock_form_manager_instance = mock_form_manager.return_value
        mock_form_manager_instance.create_form.return_value = MagicMock(form_id="test_form_id")
        
        mock_form_factory_instance = mock_form_factory.return_value
        mock_form_factory_instance.discover_forms.return_value = None
        mock_form_factory_instance.get_available_form_types.return_value = [
            ("ICS-213", "General Message"),
            ("ICS-214", "Activity Log")
        ]
        
        # Mock available form types
        self.app_controller.get_available_form_types = MagicMock(return_value=[
            ("ICS-213", "General Message"),
            ("ICS-214", "Activity Log")
        ])
        
        # Create the dialog directly for testing
        dialog = FormSelectionDialog(self.app_controller.get_available_form_types())
        
        # Simulate selecting the first item
        dialog.list_widget.setCurrentRow(0)
        
        # Get the selected type
        selected_type = dialog.get_selected_type()
        self.assertIsNone(selected_type)  # None until accept() is called
        
        # Simulate accept
        dialog.accept()
        selected_type = dialog.get_selected_type()
        
        self.assertEqual(selected_type, "ICS-213")
    
    @patch('radioforms.controllers.forms_controller.FormFactory')
    @patch('radioforms.controllers.forms_controller.FormManager')
    def test_form_operations(self, mock_form_manager, mock_form_factory):
        """Test form operations through the controller."""
        # Setup mocks
        mock_form = MagicMock(form_id="test_form_id", form_type="ICS-213")
        mock_form_manager_instance = mock_form_manager.return_value
        mock_form_manager_instance.create_form.return_value = mock_form
        mock_form_manager_instance.save_form.return_value = "/path/to/saved/form.json"
        
        mock_form_factory_instance = mock_form_factory.return_value
        mock_form_factory_instance.get_available_form_types.return_value = [
            ("ICS-213", "General Message"),
            ("ICS-214", "Activity Log")
        ]
        
        # Set forms_controller on the app_controller
        self.app_controller.forms_controller.form_factory = mock_form_factory_instance
        self.app_controller.forms_controller.form_manager = mock_form_manager_instance
        
        # Test creating a form
        form = self.app_controller.create_form("ICS-213")
        self.assertEqual(form, mock_form)
        mock_form_manager_instance.create_form.assert_called_once_with("ICS-213")
        
        # Test saving a form
        path = self.app_controller.save_form("test_form_id")
        self.assertEqual(path, "/path/to/saved/form.json")
        mock_form_manager_instance.save_form.assert_called_once()


if __name__ == '__main__':
    unittest.main()
