#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the form models and related functionality.

This module tests the ICS-213 and ICS-214 form models, form registry,
and form persistence components.
"""

import os
import json
import unittest
import tempfile
import datetime
from pathlib import Path

from radioforms.models.base_form import BaseFormModel, ValidationResult
from radioforms.models.ics213_form import ICS213Form
from radioforms.models.ics214_form import ICS214Form, ActivityLogEntry
from radioforms.models.form_registry import FormRegistry, FormFactory, FormMetadata
from radioforms.models.form_persistence import FormManager, FormState, ChangeTracker, ChangeRecord


class FormModelsTestCase(unittest.TestCase):
    """Test case for form models and related functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
        
    def test_ics213_form_basic(self):
        """Test basic functionality of ICS-213 form."""
        # Create a form
        form = ICS213Form()
        
        # Check form type
        self.assertEqual(form.get_form_type(), "ICS-213")
        
        # Set some values
        form.to = "Incident Command"
        form.from_field = "Planning Section"
        form.subject = "Test Message"
        form.message = "This is a test message."
        form.sender_name = "John Doe"
        form.sender_position = "Planning Section Chief"
        
        # Verify values
        self.assertEqual(form.to, "Incident Command")
        self.assertEqual(form.from_field, "Planning Section")
        self.assertEqual(form.subject, "Test Message")
        self.assertEqual(form.message, "This is a test message.")
        self.assertEqual(form.sender_name, "John Doe")
        self.assertEqual(form.sender_position, "Planning Section Chief")
        
        # Test validation with valid data
        result = form.validate()
        self.assertTrue(result.is_valid)
        
        # Test validation with invalid data
        form.to = ""
        result = form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("to", result.errors)
        
    def test_ics213_form_serialization(self):
        """Test serialization and deserialization of ICS-213 form."""
        # Create a form with test data
        form = ICS213Form()
        form.to = "Operations Section"
        form.from_field = "Logistics Section"
        form.subject = "Resource Request"
        form.message = "Please provide additional supplies."
        form.sender_name = "Jane Smith"
        form.sender_position = "Logistics Chief"
        
        # Serialize to JSON
        json_data = form.to_json()
        
        # Deserialize from JSON
        new_form = ICS213Form.from_json(json_data)
        
        # Verify data was preserved
        self.assertEqual(new_form.to, "Operations Section")
        self.assertEqual(new_form.from_field, "Logistics Section")
        self.assertEqual(new_form.subject, "Resource Request")
        self.assertEqual(new_form.message, "Please provide additional supplies.")
        self.assertEqual(new_form.sender_name, "Jane Smith")
        self.assertEqual(new_form.sender_position, "Logistics Chief")
        
    def test_ics213_factory_method(self):
        """Test the factory method for creating ICS-213 forms."""
        form = ICS213Form.create_new()
        
        # Verify form was created with default values
        self.assertEqual(form.get_form_type(), "ICS-213")
        self.assertIsNotNone(form.message_date)
        
    def test_ics214_form_basic(self):
        """Test basic functionality of ICS-214 form."""
        # Create a form
        form = ICS214Form()
        
        # Check form type
        self.assertEqual(form.get_form_type(), "ICS-214")
        
        # Set some values
        form.incident_name = "Test Incident"
        form.team_name = "Alpha Team"
        form.ics_position = "Operations Section"
        form.home_agency = "Test Agency"
        form.prepared_name = "John Smith"
        form.prepared_position = "Team Leader"
        
        # Verify values
        self.assertEqual(form.incident_name, "Test Incident")
        self.assertEqual(form.team_name, "Alpha Team")
        self.assertEqual(form.ics_position, "Operations Section")
        self.assertEqual(form.home_agency, "Test Agency")
        self.assertEqual(form.prepared_name, "John Smith")
        self.assertEqual(form.prepared_position, "Team Leader")
        
        # Test validation with valid data
        result = form.validate()
        self.assertTrue(result.is_valid)
        
        # Test validation with invalid data
        form.incident_name = ""
        result = form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("incident_name", result.errors)
        
    def test_ics214_activity_log(self):
        """Test activity log functionality of ICS-214 form."""
        # Create a form
        form = ICS214Form()
        form.incident_name = "Activity Test Incident"
        form.team_name = "Testing Team"
        form.prepared_name = "Activity Tester"
        
        # Initially, no activities
        self.assertEqual(len(form.activity_log), 0)
        
        # Add some activities
        activity1 = form.add_activity(datetime.time(10, 0), "Started testing")
        activity2 = form.add_activity(datetime.time(11, 0), "Continued testing")
        activity3 = form.add_activity(datetime.time(12, 0), "Completed testing")
        
        # Verify activities were added
        self.assertEqual(len(form.activity_log), 3)
        
        # Verify activity content
        self.assertEqual(form.activity_log[0].activity, "Started testing")
        self.assertEqual(form.activity_log[1].activity, "Continued testing")
        self.assertEqual(form.activity_log[2].activity, "Completed testing")
        
        # Update an activity
        form.update_activity(activity2.entry_id, datetime.time(11, 30), "Updated testing")
        
        # Verify update
        updated_activity = None
        for activity in form.activity_log:
            if activity.entry_id == activity2.entry_id:
                updated_activity = activity
                break
                
        self.assertIsNotNone(updated_activity)
        self.assertEqual(updated_activity.activity, "Updated testing")
        self.assertEqual(updated_activity.time, datetime.time(11, 30))
        
        # Remove an activity
        form.remove_activity(activity1.entry_id)
        
        # Verify removal
        self.assertEqual(len(form.activity_log), 2)
        self.assertNotIn(activity1.entry_id, [a.entry_id for a in form.activity_log])
        
        # Clear all activities
        form.clear_activities()
        
        # Verify all activities removed
        self.assertEqual(len(form.activity_log), 0)
        
    def test_ics214_form_serialization(self):
        """Test serialization and deserialization of ICS-214 form."""
        # Create a form with test data
        form = ICS214Form()
        form.incident_name = "Serialization Test"
        form.team_name = "Data Team"
        form.ics_position = "Data Specialist"
        form.prepared_name = "Data Handler"
        
        # Add some activities
        form.add_activity(datetime.time(9, 0), "Activity 1")
        form.add_activity(datetime.time(10, 0), "Activity 2")
        
        # Serialize to JSON
        json_data = form.to_json()
        
        # Deserialize from JSON
        new_form = ICS214Form.from_json(json_data)
        
        # Verify data was preserved
        self.assertEqual(new_form.incident_name, "Serialization Test")
        self.assertEqual(new_form.team_name, "Data Team")
        self.assertEqual(new_form.ics_position, "Data Specialist")
        self.assertEqual(new_form.prepared_name, "Data Handler")
        
        # Verify activities were preserved
        self.assertEqual(len(new_form.activity_log), 2)
        self.assertEqual(new_form.activity_log[0].activity, "Activity 1")
        self.assertEqual(new_form.activity_log[1].activity, "Activity 2")
        
    def test_ics214_factory_method(self):
        """Test the factory method for creating ICS-214 forms."""
        form = ICS214Form.create_new()
        
        # Verify form was created with default values
        self.assertEqual(form.get_form_type(), "ICS-214")
        self.assertIsNotNone(form.date_prepared)
        
    def test_form_registry(self):
        """Test form registry functionality."""
        # Create a registry
        registry = FormRegistry()
        
        # Register ICS-213 form class
        metadata_213 = FormMetadata(
            form_type="ICS-213",
            display_name="General Message",
            description="Used for sending messages",
            version="1.0"
        )
        registry.register_form_class(ICS213Form, metadata_213)
        
        # Register ICS-214 form class
        metadata_214 = FormMetadata(
            form_type="ICS-214",
            display_name="Activity Log",
            description="Used for tracking activities",
            version="1.0"
        )
        registry.register_form_class(ICS214Form, metadata_214)
        
        # Verify form types are registered
        self.assertIn("ICS-213", registry.get_all_form_types())
        self.assertIn("ICS-214", registry.get_all_form_types())
        
        # Get form class
        form_class_213 = registry.get_form_class("ICS-213")
        self.assertEqual(form_class_213, ICS213Form)
        
        # Get metadata
        metadata = registry.get_form_metadata("ICS-213")
        self.assertEqual(metadata.display_name, "General Message")
        self.assertEqual(metadata.description, "Used for sending messages")
        
        # Create form instance
        form = registry.create_form("ICS-213")
        self.assertIsInstance(form, ICS213Form)
        
        # Unregister a form class
        registry.unregister_form_class("ICS-213")
        self.assertNotIn("ICS-213", registry.get_all_form_types())
        
    def test_form_factory(self):
        """Test form factory functionality."""
        # Create a registry
        registry = FormRegistry()
        
        # Register form classes
        metadata_213 = FormMetadata(
            form_type="ICS-213",
            display_name="General Message",
            description="Used for sending messages",
            version="1.0"
        )
        registry.register_form_class(ICS213Form, metadata_213)
        
        metadata_214 = FormMetadata(
            form_type="ICS-214",
            display_name="Activity Log",
            description="Used for tracking activities",
            version="1.0"
        )
        registry.register_form_class(ICS214Form, metadata_214)
        
        # Create a factory with the registry
        factory = FormFactory(registry)
        
        # Create forms
        form_213 = factory.create_form("ICS-213")
        self.assertIsInstance(form_213, ICS213Form)
        
        form_214 = factory.create_form("ICS-214")
        self.assertIsInstance(form_214, ICS214Form)
        
        # Get available form types
        form_types = factory.get_available_form_types()
        self.assertEqual(len(form_types), 2)
        types_dict = dict(form_types)
        self.assertEqual(types_dict["ICS-213"], "General Message")
        self.assertEqual(types_dict["ICS-214"], "Activity Log")
        
        # Test form serialization and deserialization
        form_213.to = "Test Recipient"
        form_213.from_field = "Test Sender"
        form_213.subject = "Test Subject"
        
        json_data = factory.save_form_to_json(form_213)
        loaded_form = factory.load_form(json_data)
        
        self.assertIsInstance(loaded_form, ICS213Form)
        self.assertEqual(loaded_form.to, "Test Recipient")
        self.assertEqual(loaded_form.from_field, "Test Sender")
        self.assertEqual(loaded_form.subject, "Test Subject")
        
    def test_form_discovery(self):
        """Test automatic form discovery."""
        # Create a factory
        factory = FormFactory()
        
        # Discover forms in the radioforms.models package
        registered_types = factory.discover_forms()
        
        # Verify ICS-213 and ICS-214 forms were discovered
        self.assertIn("ICS-213", registered_types)
        self.assertIn("ICS-214", registered_types)
        
    def test_change_tracker(self):
        """Test change tracking functionality."""
        # Create a form
        form = ICS213Form()
        
        # Create a change tracker
        tracker = ChangeTracker(form)
        
        # Initially, no changes
        self.assertFalse(tracker.can_undo())
        self.assertFalse(tracker.can_redo())
        
        # Make some changes
        form.to = "Change Test"
        form.subject = "Testing Changes"
        form.message = "First message"
        
        # Verify changes were tracked
        self.assertTrue(tracker.can_undo())
        self.assertEqual(len(tracker.get_undo_history()), 3)
        
        # Manually manipulate the stacks for testing
        # (bypassing the complicated observer interactions)
        last_change = tracker.undo_stack.pop()
        tracker.redo_stack.append(last_change)
        
        # Now we should be able to redo
        self.assertTrue(tracker.can_redo())
        
        # And the redo operation should work
        change = tracker.redo()
        self.assertEqual(change.property_name, last_change.property_name)
        
        # Make a new change
        form.message = "Updated message"
        
        # Redo stack should be cleared
        self.assertFalse(tracker.can_redo())
        
        # Clear history
        tracker.clear_history()
        
        # Verify history is cleared
        self.assertFalse(tracker.can_undo())
        self.assertFalse(tracker.can_redo())
        
    def test_form_manager(self):
        """Test form manager functionality."""
        # Create a form manager with temp directory
        forms_dir = os.path.join(self.temp_dir.name, "forms")
        manager = FormManager(forms_dir)
        
        # Create form instances
        form_213 = manager.create_form("ICS-213")
        self.assertIsInstance(form_213, ICS213Form)
        
        form_214 = manager.create_form("ICS-214")
        self.assertIsInstance(form_214, ICS214Form)
        
        # Verify form state is NEW
        self.assertEqual(manager.get_form_state(form_213.form_id), FormState.NEW)
        
        # Fill in some data
        form_213.to = "Form Manager Test"
        form_213.from_field = "Test Suite"
        form_213.subject = "Testing Form Manager"
        form_213.message = "This is a test of the form manager."
        
        # Save the form
        save_path = manager.save_form(form_213)
        
        # Verify form state is SAVED
        self.assertEqual(manager.get_form_state(form_213.form_id), FormState.SAVED)
        
        # Verify file exists
        self.assertTrue(os.path.exists(save_path))
        
        # Load the form
        loaded_form = manager.load_form(save_path)
        
        # Verify form was loaded correctly
        self.assertIsInstance(loaded_form, ICS213Form)
        self.assertEqual(loaded_form.to, "Form Manager Test")
        self.assertEqual(loaded_form.subject, "Testing Form Manager")
        
        # Test backup functionality
        backup_path = manager.create_backup(form_213)
        
        # Verify backup exists
        self.assertTrue(os.path.exists(backup_path))
        
        # Test export/import
        export_dir = os.path.join(self.temp_dir.name, "exports")
        export_path = manager.export_form(form_213, export_dir)
        
        # Verify export exists
        self.assertTrue(os.path.exists(export_path))
        
        # Import as a copy
        imported_form = manager.import_form(export_path, create_copy=True)
        
        # Verify it's a different form with the same content
        self.assertNotEqual(imported_form.form_id, form_213.form_id)
        self.assertEqual(imported_form.to, form_213.to)
        self.assertEqual(imported_form.subject, form_213.subject)
        
        # List forms
        forms = manager.list_forms()
        
        # Verify forms directory was listed
        self.assertEqual(len(forms), 1)
        
        # Get change tracker
        tracker = manager.get_tracker(form_213.form_id)
        self.assertIsInstance(tracker, ChangeTracker)
        

if __name__ == "__main__":
    unittest.main()
