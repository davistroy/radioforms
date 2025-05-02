#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the Form Model Registry.

This module contains unit tests for the FormModelRegistry class to ensure
proper form management, registration, persistence, and retrieval.
"""

import os
import unittest
import tempfile
import shutil
import json
import datetime
from unittest.mock import MagicMock, patch
from pathlib import Path

from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.database.db_manager import DBManager
from radioforms.database.dao.form_dao_refactored import FormDAO


class MockForm:
    """Mock form class for testing."""
    
    def __init__(self, **kwargs):
        """Initialize with provided attributes."""
        self.__dict__.update(kwargs)
        
        # Set default values
        if 'form_id' not in kwargs:
            self.form_id = "test_form_id"
        if 'form_type' not in kwargs:
            self.form_type = "TEST_FORM"
        if 'state' not in kwargs:
            self.state = "draft"
        if 'created_at' not in kwargs:
            self.created_at = datetime.datetime.now()
        if 'updated_at' not in kwargs:
            self.updated_at = datetime.datetime.now()


class TestFormModelRegistry(unittest.TestCase):
    """Unit tests for the Form Model Registry."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test database path
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # Create db manager
        self.db_manager = DBManager(self.db_path)
        self.db_manager.init_db()
        
        # Create form DAO
        self.form_dao = FormDAO(self.db_manager)
        
        # Get form registry instance and reset any previous instance
        FormModelRegistry._instance = None
        self.form_registry = FormModelRegistry.get_instance()
        self.form_registry.set_form_dao(self.form_dao)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Close database connection
        self.db_manager.close()
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
        # Reset form registry instance
        FormModelRegistry._instance = None
        
    def test_singleton_pattern(self):
        """Test that FormModelRegistry follows the singleton pattern."""
        # Get another instance
        another_registry = FormModelRegistry.get_instance()
        
        # Verify it's the same instance
        self.assertIs(self.form_registry, another_registry)
        
    def test_register_form_type(self):
        """Test registering form types."""
        # Register a form type
        self.form_registry.register_form_type("TEST_FORM", MockForm)
        
        # Verify type was registered
        form_types = self.form_registry.get_registered_types()
        self.assertIn("TEST_FORM", form_types)
        
    def test_create_form(self):
        """Test creating forms."""
        # Register a form type
        self.form_registry.register_form_type("TEST_FORM", MockForm)
        
        # Create a form
        form = self.form_registry.create_form("TEST_FORM")
        
        # Verify form was created correctly
        self.assertIsInstance(form, MockForm)
        self.assertEqual(form.form_type, "TEST_FORM")
        self.assertEqual(form.state, "draft")
        self.assertIsNotNone(form.form_id)
        self.assertIsNotNone(form.created_at)
        self.assertIsNotNone(form.updated_at)
        
        # Try to create a non-registered form type
        form = self.form_registry.create_form("NONEXISTENT_TYPE")
        self.assertIsNone(form)
        
    def test_save_load_form(self):
        """Test saving and loading forms."""
        # Register a form type
        self.form_registry.register_form_type("TEST_FORM", MockForm)
        
        # Create a form with specific data
        form = MockForm(
            form_id="test_id_123",
            form_type="TEST_FORM",
            test_field="test_value",
            int_field=42,
            date_field=datetime.date(2025, 4, 30)
        )
        
        # Mock the DAO
        mock_form_dao = MagicMock()
        self.form_registry.set_form_dao(mock_form_dao)
        
        # Create the expected data dictionary for the form
        expected_data = json.dumps({
            "test_field": "test_value",
            "int_field": 42,
            "date_field": "2025-04-30"
        })
        
        # Set up mock behavior
        mock_form_dao.find_by_id.return_value = None  # Act like form doesn't exist yet
        
        # Save the form
        form_id = self.form_registry.save_form(form)
        
        # Verify DAO was called correctly
        self.assertEqual(form_id, "test_id_123")
        mock_form_dao.find_by_id.assert_called_with("test_id_123")
        
        # Ensure create was called
        mock_form_dao.create.assert_called()
        
        # Only check call_args if create was actually called
        if mock_form_dao.create.call_args is not None:
            create_call_args = mock_form_dao.create.call_args[0][0]
            self.assertEqual(create_call_args["form_id"], "test_id_123")
            self.assertEqual(create_call_args["form_type"], "TEST_FORM")
            self.assertEqual(create_call_args["state"], "draft")
            self.assertIn("data", create_call_args)
        
        # Now test loading a form
        mock_form_dao.find_by_id.return_value = {
            "form_id": "test_id_123",
            "form_type": "TEST_FORM",
            "state": "approved",
            "data": expected_data,
            "created_at": "2025-04-30T12:00:00",
            "updated_at": "2025-04-30T12:30:00"
        }
        
        # Load the form
        loaded_form = self.form_registry.load_form("test_id_123")
        
        # Verify form was loaded correctly
        self.assertIsInstance(loaded_form, MockForm)
        self.assertEqual(loaded_form.form_id, "test_id_123")
        self.assertEqual(loaded_form.form_type, "TEST_FORM")
        self.assertEqual(loaded_form.state, "approved")
        self.assertEqual(loaded_form.test_field, "test_value")
        self.assertEqual(loaded_form.int_field, 42)
        self.assertEqual(loaded_form.date_field, "2025-04-30")
        self.assertEqual(loaded_form.created_at, "2025-04-30T12:00:00")
        self.assertEqual(loaded_form.updated_at, "2025-04-30T12:30:00")
        
    def test_find_forms(self):
        """Test finding forms by criteria."""
        # Register a form type
        self.form_registry.register_form_type("TEST_FORM", MockForm)
        
        # Mock the DAO
        mock_form_dao = MagicMock()
        self.form_registry.set_form_dao(mock_form_dao)
        
        # Set up the mock to return some forms
        form_data = [
            {
                "form_id": "test_id_1",
                "form_type": "TEST_FORM",
                "state": "draft",
                "data": '{"test_field": "value1"}'
            },
            {
                "form_id": "test_id_2",
                "form_type": "TEST_FORM",
                "state": "approved",
                "data": '{"test_field": "value2"}'
            }
        ]
        mock_form_dao.find_by_fields.return_value = form_data
        
        # Set up a mock for load_form that will be called when converting to objects
        self.form_registry.load_form = MagicMock()
        
        # Find forms
        criteria = {"form_type": "TEST_FORM"}
        forms = self.form_registry.find_forms(criteria)
        
        # Verify DAO was called correctly
        mock_form_dao.find_by_fields.assert_called_once_with(criteria, as_dict=True)
        
        # Verify results - for dictionary return
        forms_dict = self.form_registry.find_forms(criteria, as_dict=True)
        self.assertEqual(len(forms_dict), 2)
        self.assertEqual(forms_dict[0]["form_id"], "test_id_1")
        self.assertEqual(forms_dict[1]["form_id"], "test_id_2")
        
    def test_delete_form(self):
        """Test deleting a form."""
        # Mock the DAO
        mock_form_dao = MagicMock()
        self.form_registry.set_form_dao(mock_form_dao)
        mock_form_dao.delete.return_value = True
        
        # Delete a form
        result = self.form_registry.delete_form("test_id_123")
        
        # Verify DAO was called correctly
        mock_form_dao.delete.assert_called_once_with("test_id_123")
        self.assertTrue(result)
        
    def test_builtin_types(self):
        """Test built-in form type registration."""
        # The registry should automatically register built-in types
        form_types = self.form_registry.get_registered_types()
        
        # Verify ICS-213 and ICS-214 are registered
        self.assertIn("ICS-213", form_types)
        self.assertIn("ICS-214", form_types)
        
    def test_no_dao_set(self):
        """Test behavior when no DAO is set."""
        # Create a new registry instance without setting a DAO
        FormModelRegistry._instance = None
        registry = FormModelRegistry.get_instance()
        
        # Register a form type
        registry.register_form_type("TEST_FORM", MockForm)
        
        # Create a form
        form = registry.create_form("TEST_FORM")
        
        # Verify actions that require a DAO return expected values
        self.assertIsNone(registry.save_form(form))
        self.assertIsNone(registry.load_form("test_id"))
        self.assertEqual(registry.find_forms({}), [])
        self.assertFalse(registry.delete_form("test_id"))


if __name__ == "__main__":
    unittest.main()
