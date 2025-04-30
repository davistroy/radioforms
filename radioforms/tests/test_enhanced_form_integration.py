#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration tests for enhanced form models.

This module contains integration tests for the enhanced form models with the
DAO layer, Form Model Registry, and form persistence operations.
"""

import unittest
import os
import datetime
import tempfile
from unittest.mock import MagicMock, patch

from radioforms.models.enhanced_ics213_form import EnhancedICS213Form, FormState as ICS213FormState
from radioforms.models.enhanced_ics214_form import EnhancedICS214Form, FormState as ICS214FormState, ActivityLogEntry
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.database.dao.attachment_dao_refactored import AttachmentDAO


class TestEnhancedFormIntegration(unittest.TestCase):
    """Integration tests for enhanced form models with DAO layer."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create mock DAOs
        self.form_dao = MagicMock(spec=FormDAO)
        self.attachment_dao = MagicMock(spec=AttachmentDAO)
        
        # Set up registry
        self.registry = FormModelRegistry.get_instance()
        self.registry.set_form_dao(self.form_dao)
        
    def test_registry_initialization(self):
        """Test that the registry is properly initialized with form types."""
        # Check that standard form types are registered
        registered_types = self.registry.get_registered_types()
        self.assertIn("ICS-213", registered_types)
        self.assertIn("ICS-214", registered_types)
        
        # Verify model classes
        ics213_class = self.registry.get_model_class("ICS-213")
        ics214_class = self.registry.get_model_class("ICS-214")
        
        self.assertEqual(ics213_class, EnhancedICS213Form)
        self.assertEqual(ics214_class, EnhancedICS214Form)
        
    def test_form_creation_with_registry(self):
        """Test creating forms through the registry."""
        # Configure mock
        self.form_dao.create.return_value = "123"
        
        # Create forms through registry
        ics213 = self.registry.create_form("ICS-213")
        ics214 = self.registry.create_form("ICS-214")
        
        # Verify the forms
        self.assertIsInstance(ics213, EnhancedICS213Form)
        self.assertIsInstance(ics214, EnhancedICS214Form)
        
        # Create with DAO
        ics213_dao = self.registry.create_form_with_dao("ICS-213")
        
        # Verify interaction with DAO
        self.assertEqual(ics213_dao.form_id, "123")
        self.form_dao.create.assert_called()
        
    def test_form_persistence_workflow(self):
        """Test a complete workflow of form creation, saving, and loading."""
        # Configure mocks
        self.form_dao.create.return_value = "123"
        
        # Create and configure form data for ICS-213
        ics213 = self.registry.create_form("ICS-213")
        ics213.to = "John Doe"
        ics213.from_field = "Jane Smith"
        ics213.subject = "Resource Request"
        ics213.message = "We need additional supplies."
        ics213.sender_name = "Jane Smith"
        
        # Save the form
        form_id = self.registry.save_form(ics213)
        self.assertEqual(form_id, "123")
        
        # Configure mock for loading
        self.form_dao.find_by_id.return_value = {
            "form_id": "123",
            "form_type": "ICS-213",
            "to": "John Doe",
            "from": "Jane Smith",
            "subject": "Resource Request",
            "message": "We need additional supplies.",
            "sender_name": "Jane Smith"
        }
        
        # Load the form
        loaded_form = self.registry.load_form("123")
        
        # Verify loaded form
        self.assertIsInstance(loaded_form, EnhancedICS213Form)
        self.assertEqual(loaded_form.to, "John Doe")
        self.assertEqual(loaded_form.from_field, "Jane Smith")
        self.assertEqual(loaded_form.subject, "Resource Request")
        self.assertEqual(loaded_form.message, "We need additional supplies.")
        
    def test_ics214_activity_log_persistence(self):
        """Test persisting and loading ICS-214 with activity log entries."""
        # Configure mocks
        self.form_dao.create.return_value = "456"
        
        # Create and configure form data for ICS-214
        ics214 = self.registry.create_form("ICS-214")
        ics214.incident_name = "Test Incident"
        ics214.team_name = "Operations Team Alpha"
        
        # Add activities
        ics214.add_activity(time=datetime.time(8, 0), activity="Morning briefing", notable=True)
        ics214.add_activity(time=datetime.time(12, 0), activity="Resource deployment")
        
        # Add personnel
        ics214.add_personnel("John Doe", "Team Lead", "Agency A")
        
        # Save the form
        form_id = self.registry.save_form(ics214)
        self.assertEqual(form_id, "456")
        
        # Capture the saved data for verification
        saved_dict = self.form_dao.create.call_args[0][0]
        self.assertEqual(saved_dict["incident_name"], "Test Incident")
        self.assertEqual(saved_dict["team_name"], "Operations Team Alpha")
        self.assertEqual(len(saved_dict["activity_log"]), 2)
        self.assertEqual(saved_dict["activity_log"][0]["activity"], "Morning briefing")
        self.assertTrue(saved_dict["activity_log"][0]["notable"])
        self.assertEqual(len(saved_dict["personnel"]), 1)
        self.assertEqual(saved_dict["personnel"][0]["name"], "John Doe")
        
        # Configure mock for loading
        self.form_dao.find_by_id.return_value = saved_dict
        
        # Load the form
        loaded_form = self.registry.load_form("456")
        
        # Verify loaded form
        self.assertIsInstance(loaded_form, EnhancedICS214Form)
        self.assertEqual(loaded_form.incident_name, "Test Incident")
        self.assertEqual(loaded_form.team_name, "Operations Team Alpha")
        self.assertEqual(len(loaded_form.activity_log), 2)
        self.assertEqual(loaded_form.activity_log[0].activity, "Morning briefing")
        self.assertTrue(loaded_form.activity_log[0].notable)
        self.assertEqual(len(loaded_form.personnel), 1)
        self.assertEqual(loaded_form.personnel[0]["name"], "John Doe")
        
    def test_form_templates(self):
        """Test getting form templates."""
        # Get templates
        ics213_template = self.registry.get_form_template("ICS-213")
        ics214_template = self.registry.get_form_template("ICS-214")
        
        # Verify the templates
        self.assertIsInstance(ics213_template, EnhancedICS213Form)
        self.assertIsNone(ics213_template.form_id)  # Should not have an ID
        self.assertEqual(ics213_template.state, ICS213FormState.DRAFT)
        
        self.assertIsInstance(ics214_template, EnhancedICS214Form)
        self.assertIsNone(ics214_template.form_id)  # Should not have an ID
        self.assertEqual(ics214_template.state, ICS214FormState.DRAFT)
        
        # DAO should not be called
        self.form_dao.create.assert_not_called()
        
    def test_find_forms(self):
        """Test finding forms with criteria."""
        # Configure mock
        self.form_dao.find_by.return_value = [
            {
                "form_id": "123",
                "form_type": "ICS-213",
                "to": "John Doe",
                "state": "draft"
            },
            {
                "form_id": "124",
                "form_type": "ICS-213",
                "to": "Jane Smith",
                "state": "approved"
            }
        ]
        
        # Find forms as dictionaries
        forms = self.registry.find_forms({"form_type": "ICS-213"}, as_dict=True)
        
        # Verify results
        self.assertEqual(len(forms), 2)
        self.assertEqual(forms[0]["form_id"], "123")
        self.assertEqual(forms[1]["form_id"], "124")
        
        # Find forms as objects
        self.form_dao.find_by.reset_mock()
        self.form_dao.find_by.return_value = [
            {
                "form_id": "456",
                "form_type": "ICS-214",
                "incident_name": "Test Incident",
                "state": "finalized"
            }
        ]
        
        forms = self.registry.find_forms({"form_type": "ICS-214"}, as_dict=False)
        
        # Verify results
        self.assertEqual(len(forms), 1)
        self.assertIsInstance(forms[0], EnhancedICS214Form)
        self.assertEqual(forms[0].form_id, "456")
        self.assertEqual(forms[0].incident_name, "Test Incident")
        self.assertEqual(forms[0].state, ICS214FormState.FINALIZED)
        
    def test_form_version_management(self):
        """Test form version management."""
        # Configure mock for version creation
        self.form_dao.find_by_id.return_value = {
            "form_id": "123", 
            "form_type": "ICS-213",
            "version": 1
        }
        self.form_dao.create_version = MagicMock()
        
        # Create a form and update it
        form = EnhancedICS213Form(form_id="123")
        self.registry.save_form(form, create_version=True)
        
        # Verify version creation was called
        self.form_dao.create_version.assert_called_once()
        
        # Configure mock for version retrieval
        self.form_dao.find_version_by_id = MagicMock(return_value={
            "form_id": "123",
            "form_type": "ICS-213",
            "version": 2,
            "to": "Version 2"
        })
        
        # Load a specific version
        versioned_form = self.registry.load_form("123", version_id="v2")
        
        # Verify version was loaded
        self.assertEqual(versioned_form.to, "Version 2")
        self.form_dao.find_version_by_id.assert_called_once_with("v2")
        
    def test_form_state_transitions(self):
        """Test form state transitions with persistence."""
        # Configure mock
        self.form_dao.create.return_value = "123"
        self.form_dao.find_by_id.return_value = {"form_id": "123", "form_type": "ICS-213"}
        
        # Create an ICS-213 form
        form = EnhancedICS213Form()
        form.to = "John Doe"
        form.from_field = "Jane Smith"
        form.subject = "Resource Request"
        form.message = "We need additional supplies."
        
        # Save initial state
        form_id = form.save_to_dao(self.form_dao)
        self.assertEqual(form_id, "123")
        
        # Transition to approved state
        form.approve("Jane Smith", "Operations Chief", "JSmith")
        
        # Save updated state
        form.save_to_dao(self.form_dao)
        
        # Verify update was called with new state
        call_args = self.form_dao.update.call_args[0][0]
        self.assertEqual(call_args["state"], "approved")
        self.assertEqual(call_args["sender_name"], "Jane Smith")
        self.assertEqual(call_args["sender_position"], "Operations Chief")
        self.assertEqual(call_args["sender_signature"], "JSmith")
        
    def test_custom_form_registration(self):
        """Test registering and using a custom form type."""
        # Create a test form class (Mock)
        test_form_class = MagicMock()
        test_form_instance = MagicMock()
        test_form_class.return_value = test_form_instance
        test_form_class.create_with_dao.return_value = test_form_instance
        
        # Register the test form
        self.registry.register_model("TEST-FORM", test_form_class)
        
        # Verify registration
        registered_types = self.registry.get_registered_types()
        self.assertIn("TEST-FORM", registered_types)
        
        # Create a form of the test type
        form = self.registry.create_form("TEST-FORM")
        self.assertEqual(form, test_form_instance)
        
        # Unregister the test form
        self.registry.unregister_model("TEST-FORM")
        
        # Verify unregistration
        registered_types = self.registry.get_registered_types()
        self.assertNotIn("TEST-FORM", registered_types)


class TestEnhancedFormRealDAOIntegration(unittest.TestCase):
    """
    Integration tests for enhanced form models with real DAOs.
    
    These tests use a temporary SQLite database to test the integration
    with actual DAO implementations.
    """
    
    @unittest.skip("Needs real database setup")
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Initialize DAOs with the temporary database
        # Note: This requires actual DAO initialization code which depends on
        # your database setup. Adjust as needed.
        # self.form_dao = FormDAO(self.db_path)
        # self.attachment_dao = AttachmentDAO(self.db_path)
        
        # Set up registry
        self.registry = FormModelRegistry.get_instance()
        # self.registry.set_form_dao(self.form_dao)
        
    @unittest.skip("Needs real database setup")    
    def tearDown(self):
        """Tear down test fixtures after each test."""
        # Close and remove the temporary database
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
    @unittest.skip("Needs real database setup")    
    def test_real_db_persistence(self):
        """
        Test persistence with a real database.
        
        This test is skipped by default since it requires a real database setup.
        Enable it when testing with an actual database backend.
        """
        # Create an ICS-213 form
        form = self.registry.create_form("ICS-213")
        form.to = "John Doe"
        form.from_field = "Jane Smith"
        form.subject = "Resource Request"
        form.message = "We need additional supplies."
        
        # Save the form
        form_id = self.registry.save_form(form)
        
        # Load the form
        loaded_form = self.registry.load_form(form_id)
        
        # Verify loaded form
        self.assertEqual(loaded_form.to, "John Doe")
        self.assertEqual(loaded_form.from_field, "Jane Smith")
        self.assertEqual(loaded_form.subject, "Resource Request")
        self.assertEqual(loaded_form.message, "We need additional supplies.")
        

if __name__ == '__main__':
    unittest.main()
