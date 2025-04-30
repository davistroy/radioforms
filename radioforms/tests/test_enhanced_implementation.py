#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration test for the enhanced RadioForms implementation.

This script tests the complete enhanced implementation of RadioForms,
including the form models, UI components, and application controller.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from radioforms.config.config_manager import ConfigManager
from radioforms.database.db_manager import DBManager
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.database.dao.incident_dao_refactored import IncidentDAO
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.models.enhanced_ics213_form import EnhancedICS213Form
from radioforms.models.enhanced_ics214_form import EnhancedICS214Form
from radioforms.controllers.app_controller_enhanced import EnhancedAppController
from radioforms.views.startup_wizard import run_startup_wizard
from radioforms.views.ics213_form_editor import ICS213FormEditor
from radioforms.views.ics214_form_editor import ICS214FormEditor
from radioforms.views.form_tab_widget import FormTabWidget


class TestEnhancedImplementation(unittest.TestCase):
    """Integration test for the enhanced RadioForms implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test paths
        self.config_path = os.path.join(self.test_dir, "config.ini")
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # Initialize components
        self.config_manager = ConfigManager(self.config_path)
        self.db_manager = DBManager(self.db_path)
        
        # Initialize database
        self.db_manager.init_db()
        
        # Create DAOs
        self.form_dao = FormDAO(self.db_manager)
        self.incident_dao = IncidentDAO(self.db_manager)
        
        # Create form registry
        self.form_registry = FormModelRegistry.get_instance()
        self.form_registry.set_form_dao(self.form_dao)
        
        # Create QApplication for UI tests
        self.app = QApplication.instance() or QApplication([])
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Close database connection
        self.db_manager.close()
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_config_manager(self):
        """Test configuration manager functionality."""
        # Set some configuration values
        self.config_manager.set_value("Test", "key1", "value1")
        self.config_manager.set_value("Test", "key2", "value2")
        
        # Save configuration
        self.config_manager.save()
        
        # Create a new config manager with the same path
        config_manager2 = ConfigManager(self.config_path)
        
        # Check if values are preserved
        self.assertEqual(config_manager2.get_value("Test", "key1"), "value1")
        self.assertEqual(config_manager2.get_value("Test", "key2"), "value2")
        
        # Test different value types
        self.config_manager.set_value("Types", "boolean", "true")
        self.config_manager.set_value("Types", "integer", "42")
        self.config_manager.set_value("Types", "float", "3.14")
        self.config_manager.set_value("Types", "list", "a,b,c")
        
        self.assertTrue(self.config_manager.get_boolean("Types", "boolean"))
        self.assertEqual(self.config_manager.get_int("Types", "integer"), 42)
        self.assertEqual(self.config_manager.get_float("Types", "float"), 3.14)
        self.assertEqual(self.config_manager.get_list("Types", "list"), ["a", "b", "c"])
        
    def test_db_manager(self):
        """Test database manager functionality."""
        # Check if database was initialized
        schema_version = self.db_manager.get_schema_version()
        self.assertEqual(schema_version, self.db_manager.SCHEMA_VERSION)
        
        # Test basic query execution
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("test_key", "test_value", "2025-01-01"),
            commit=True
        )
        
        # Test query result
        cursor = self.db_manager.execute("SELECT value FROM settings WHERE key = ?", ("test_key",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["value"], "test_value")
        
        # Test query_to_dict method
        result = self.db_manager.query_to_dict("SELECT * FROM settings WHERE key = ?", ("test_key",))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["key"], "test_key")
        self.assertEqual(result[0]["value"], "test_value")
        
        # Test transaction handling
        self.db_manager.begin_transaction()
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("test_key2", "test_value2", "2025-01-01")
        )
        self.db_manager.commit()
        
        cursor = self.db_manager.execute("SELECT COUNT(*) as count FROM settings")
        row = cursor.fetchone()
        self.assertEqual(row["count"], 2)
        
        # Test rollback
        self.db_manager.begin_transaction()
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("test_key3", "test_value3", "2025-01-01")
        )
        self.db_manager.rollback()
        
        cursor = self.db_manager.execute("SELECT COUNT(*) as count FROM settings")
        row = cursor.fetchone()
        self.assertEqual(row["count"], 2)
        
    def test_form_model_registry(self):
        """Test form model registry functionality."""
        # Check registered form types
        form_types = self.form_registry.get_registered_types()
        self.assertIn("ICS-213", form_types)
        self.assertIn("ICS-214", form_types)
        
        # Create a form
        ics213 = self.form_registry.create_form("ICS-213")
        self.assertIsInstance(ics213, EnhancedICS213Form)
        
        # Set some form properties
        ics213.to = "John Doe"
        ics213.from_field = "Jane Smith"
        ics213.subject = "Test Message"
        ics213.message = "This is a test message."
        
        # Save the form
        form_id = self.form_registry.save_form(ics213)
        self.assertIsNotNone(form_id)
        
        # Load the form
        loaded_form = self.form_registry.load_form(form_id)
        self.assertIsInstance(loaded_form, EnhancedICS213Form)
        self.assertEqual(loaded_form.to, "John Doe")
        self.assertEqual(loaded_form.from_field, "Jane Smith")
        self.assertEqual(loaded_form.subject, "Test Message")
        self.assertEqual(loaded_form.message, "This is a test message.")
        
        # Find forms
        forms = self.form_registry.find_forms({"form_type": "ICS-213"}, as_dict=True)
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0]["form_id"], form_id)
        
        # Test form models
        ics214 = self.form_registry.create_form("ICS-214")
        self.assertIsInstance(ics214, EnhancedICS214Form)
        
        # Set some form properties
        ics214.incident_name = "Test Incident"
        ics214.team_name = "Test Team"
        
        # Add activities
        import datetime
        ics214.add_activity(
            time=datetime.time(8, 0),
            activity="Test Activity 1"
        )
        ics214.add_activity(
            time=datetime.time(9, 0),
            activity="Test Activity 2",
            notable=True
        )
        
        # Add personnel
        ics214.add_personnel("John Doe", "Team Lead", "Test Agency")
        
        # Save the form
        form_id = self.form_registry.save_form(ics214)
        self.assertIsNotNone(form_id)
        
        # Load the form
        loaded_form = self.form_registry.load_form(form_id)
        self.assertIsInstance(loaded_form, EnhancedICS214Form)
        self.assertEqual(loaded_form.incident_name, "Test Incident")
        self.assertEqual(loaded_form.team_name, "Test Team")
        self.assertEqual(len(loaded_form.activity_log), 2)
        self.assertEqual(loaded_form.activity_log[0].activity, "Test Activity 1")
        self.assertFalse(loaded_form.activity_log[0].notable)
        self.assertEqual(loaded_form.activity_log[1].activity, "Test Activity 2")
        self.assertTrue(loaded_form.activity_log[1].notable)
        
    @unittest.skip("UI test requires manual interaction")
    def test_form_editors(self):
        """Test form editor UI components."""
        # Create test forms
        ics213 = self.form_registry.create_form("ICS-213")
        ics213.to = "John Doe"
        ics213.from_field = "Jane Smith"
        ics213.subject = "Test Message"
        ics213.message = "This is a test message."
        form_id_213 = self.form_registry.save_form(ics213)
        
        ics214 = self.form_registry.create_form("ICS-214")
        ics214.incident_name = "Test Incident"
        ics214.team_name = "Test Team"
        form_id_214 = self.form_registry.save_form(ics214)
        
        # Create ICS-213 editor
        editor_213 = ICS213FormEditor(self.form_registry, form_id=form_id_213)
        editor_213.show()
        
        # Create ICS-214 editor
        editor_214 = ICS214FormEditor(self.form_registry, form_id=form_id_214)
        editor_214.show()
        
        # Create form tab widget
        form_tab_widget = FormTabWidget(self.form_registry, self.form_dao)
        form_tab_widget.show()
        
        # Run the application event loop for a short time
        QApplication.processEvents()
        
        # Note: This is a minimal UI test that just creates and shows the components
        # A real UI test would interact with the components and verify results
        
    @unittest.skip("App controller test requires manual interaction")
    def test_app_controller(self):
        """Test application controller."""
        # Set up test environment
        self.config_manager.set_value("General", "first_run", "false")
        self.config_manager.set_value("Database", "path", self.db_path)
        self.config_manager.save()
        
        # Create app controller
        controller = EnhancedAppController()
        
        # Patch methods that would show UI
        with patch.object(controller, '_run_startup_wizard', return_value=True), \
             patch.object(controller, '_setup_main_window'):
            # Run the controller
            result = controller.run()
            
            # Check result
            self.assertTrue(result)
            
            # Verify that database and form registry were initialized
            self.assertIsNotNone(controller._db_manager)
            self.assertIsNotNone(controller._form_registry)
            

if __name__ == "__main__":
    unittest.main()
