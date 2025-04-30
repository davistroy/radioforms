#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the API Controller module.
"""

import unittest
import tempfile
import datetime
from pathlib import Path

from PySide6.QtCore import QObject

from radioforms.database.db_manager import DatabaseManager
from radioforms.controllers.api_controller import APIController
from radioforms.database.models.incident import Incident
from radioforms.database.models.form import Form, FormStatus
from radioforms.database.models.user import User


class APIControllerTestCase(unittest.TestCase):
    """Test case for the API Controller."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_radioforms.db"
        
        # Create database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create API controller
        self.api_controller = APIController(self.db_manager)
        
        # Set up signal tracking
        self.signal_tracker = SignalTracker()
        self.api_controller.data_updated.connect(self.signal_tracker.slot_data_updated)
        
        # Create test data
        self._create_test_data()
        
    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        self.temp_dir.cleanup()
        
    def _create_test_data(self):
        """Create test data for the controller tests."""
        # Create a test user
        self.test_user_data = {
            "name": "Test User",
            "call_sign": "TEST1"
        }
        self.test_user_id = self.api_controller.create_user(self.test_user_data)
        
        # Create a test incident
        self.test_incident_data = {
            "name": "Test Incident",
            "description": "A test incident for API controller testing"
        }
        self.test_incident_id = self.api_controller.create_incident(self.test_incident_data)
        
        # Create a test form
        self.test_form_data = {
            "incident_id": self.test_incident_id,
            "form_type": "ICS-213",
            "title": "Test Message Form",
            "creator_id": self.test_user_id,
            "status": str(FormStatus.DRAFT)
        }
        
        self.test_form_content = {
            "to": "Command",
            "from": "Operations",
            "subject": "Test Message",
            "message": "This is a test message."
        }
        
        self.test_form_id = self.api_controller.create_form_with_content(
            self.test_form_data, self.test_form_content, self.test_user_id
        )
        
    def test_incident_operations(self):
        """Test incident operations in the API controller."""
        # Get active incidents
        incidents = self.api_controller.get_active_incidents()
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0]["name"], "Test Incident")
        
        # Get a specific incident
        incident = self.api_controller.get_incident(self.test_incident_id)
        self.assertIsNotNone(incident)
        self.assertEqual(incident["name"], "Test Incident")
        
        # Update an incident
        self.signal_tracker.reset()
        update_data = {"description": "Updated incident description"}
        result = self.api_controller.update_incident(self.test_incident_id, update_data)
        self.assertTrue(result)
        
        # Verify signal was emitted
        self.assertEqual(self.signal_tracker.entity_type, "incident")
        self.assertIsNotNone(self.signal_tracker.data)
        
        # Verify the update
        updated_incident = self.api_controller.get_incident(self.test_incident_id)
        self.assertEqual(updated_incident["description"], "Updated incident description")
        
        # Close an incident
        self.signal_tracker.reset()
        result = self.api_controller.close_incident(self.test_incident_id)
        self.assertTrue(result)
        
        # Verify the incident was closed (is_active would be false in the DAO layer)
        closed_incident = self.api_controller.get_incident(self.test_incident_id)
        self.assertIsNotNone(closed_incident["end_date"])
        
        # Reopen the incident
        self.signal_tracker.reset()
        result = self.api_controller.reopen_incident(self.test_incident_id)
        self.assertTrue(result)
        
        # Verify the incident was reopened
        reopened_incident = self.api_controller.get_incident(self.test_incident_id)
        self.assertIsNone(reopened_incident["end_date"])
        
        # Get incident stats
        stats = self.api_controller.get_incident_stats()
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["active"], 1)
        self.assertEqual(stats["closed"], 0)
        
    def test_form_operations(self):
        """Test form operations in the API controller."""
        # Get forms for an incident
        forms = self.api_controller.get_forms_for_incident(self.test_incident_id)
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0]["title"], "Test Message Form")
        
        # Get a specific form
        form = self.api_controller.get_form(self.test_form_id)
        self.assertIsNotNone(form)
        self.assertEqual(form["title"], "Test Message Form")
        
        # Get form with content
        form_with_content = self.api_controller.get_form_with_content(self.test_form_id)
        self.assertIsNotNone(form_with_content)
        self.assertIn("form", form_with_content)
        self.assertIn("content", form_with_content)
        self.assertEqual(form_with_content["form"]["title"], "Test Message Form")
        self.assertEqual(form_with_content["content"]["message"], "This is a test message.")
        
        # Update form with content
        self.signal_tracker.reset()
        updated_form_data = {"title": "Updated Message Form"}
        updated_content = {
            "to": "Command Post",
            "from": "Operations",
            "subject": "Updated Message",
            "message": "This is an updated test message."
        }
        
        result = self.api_controller.update_form_with_content(
            self.test_form_id, updated_form_data, updated_content, self.test_user_id
        )
        self.assertTrue(result)
        
        # Verify signal was emitted
        self.assertEqual(self.signal_tracker.entity_type, "form")
        self.assertIsNotNone(self.signal_tracker.data)
        
        # Verify the update
        updated_form = self.api_controller.get_form_with_content(self.test_form_id)
        self.assertEqual(updated_form["form"]["title"], "Updated Message Form")
        self.assertEqual(updated_form["content"]["message"], "This is an updated test message.")
        
        # Update form status
        self.signal_tracker.reset()
        result = self.api_controller.update_form_status(self.test_form_id, FormStatus.FINALIZED)
        self.assertTrue(result)
        
        # Verify the status update
        form = self.api_controller.get_form(self.test_form_id)
        self.assertEqual(form["status"], str(FormStatus.FINALIZED))
        
        # Get recent forms
        recent_forms = self.api_controller.get_recent_forms()
        self.assertEqual(len(recent_forms), 1)
        self.assertEqual(recent_forms[0]["id"], self.test_form_id)
        
    def test_validation(self):
        """Test input validation in the API controller."""
        # Test incident creation validation
        with self.assertRaises(ValueError):
            # Missing required name
            self.api_controller.create_incident({})
            
        with self.assertRaises(ValueError):
            # Invalid name type
            self.api_controller.create_incident({"name": 123})
            
        with self.assertRaises(ValueError):
            # Invalid description type
            self.api_controller.create_incident({"name": "Test", "description": 123})
            
        # Test form creation validation
        with self.assertRaises(ValueError):
            # Missing required incident_id
            self.api_controller.create_form_with_content(
                {"form_type": "ICS-213", "title": "Test"},
                {"content": "test"}
            )
            
        with self.assertRaises(ValueError):
            # Missing required form_type
            self.api_controller.create_form_with_content(
                {"incident_id": 1, "title": "Test"},
                {"content": "test"}
            )
            
        with self.assertRaises(ValueError):
            # Missing required title
            self.api_controller.create_form_with_content(
                {"incident_id": 1, "form_type": "ICS-213"},
                {"content": "test"}
            )
            
        with self.assertRaises(ValueError):
            # Invalid incident_id type
            self.api_controller.create_form_with_content(
                {"incident_id": "1", "form_type": "ICS-213", "title": "Test"},
                {"content": "test"}
            )
            
        with self.assertRaises(ValueError):
            # Empty content
            self.api_controller.create_form_with_content(
                {"incident_id": 1, "form_type": "ICS-213", "title": "Test"},
                {}
            )
            
    def test_user_operations(self):
        """Test user operations in the API controller."""
        # Get a user by ID
        user = self.api_controller.get_user(self.test_user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Test User")
        self.assertEqual(user["call_sign"], "TEST1")
        
        # Get a user by call sign
        user = self.api_controller.get_user_by_call_sign("TEST1")
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], self.test_user_id)
        
        # Create a new user
        self.signal_tracker.reset()
        new_user_data = {
            "name": "New User",
            "call_sign": "NEW1"
        }
        new_user_id = self.api_controller.create_user(new_user_data)
        self.assertIsNotNone(new_user_id)
        
        # Verify signal was emitted
        self.assertEqual(self.signal_tracker.entity_type, "user")
        self.assertIsNotNone(self.signal_tracker.data)
        
        # Verify the user was created
        new_user = self.api_controller.get_user(new_user_id)
        self.assertEqual(new_user["name"], "New User")
        self.assertEqual(new_user["call_sign"], "NEW1")


class SignalTracker(QObject):
    """Helper class to track emitted signals."""
    
    def __init__(self):
        """Initialize the signal tracker."""
        super().__init__()
        self.reset()
        
    def reset(self):
        """Reset the signal tracker."""
        self.entity_type = None
        self.data = None
        
    def slot_data_updated(self, entity_type, data):
        """Slot for the data_updated signal."""
        self.entity_type = entity_type
        self.data = data


if __name__ == "__main__":
    unittest.main()
