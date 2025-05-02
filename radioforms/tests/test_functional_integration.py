#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functional Integration Tests.

This module implements functional integration tests using the new testing approach
that focuses on verifying outcomes rather than implementation details. It demonstrates
the use of real database fixtures, robust schema versioning, and enhanced form resolution.
"""

import unittest
import os
import tempfile
import datetime
import json
import logging
from pathlib import Path

# Add parent directory to path to import RadioForms modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import test utilities
from radioforms.tests.test_utils.functional_test_utils import FunctionalTestCase, FormWorkflowTester
from radioforms.models.enhanced_form_resolver import FormTypeResolver, resolve_form_type

# Import required RadioForms modules
from radioforms.models.enhanced_ics213_form import EnhancedICS213Form
from radioforms.models.enhanced_ics214_form import EnhancedICS214Form


logger = logging.getLogger(__name__)


class TestFunctionalIntegration(FunctionalTestCase):
    """
    Functional integration tests for RadioForms.
    
    These tests demonstrate the use of real database fixtures and outcome-based
    testing to verify application behavior in a more robust way.
    """
    
    def test_enhanced_form_resolver(self):
        """
        Test enhanced form type resolution with various edge cases.
        """
        # Test with explicit form type
        form_data = {
            "form_type": "ICS-213",
            "to": "Jane Doe",
            "from": "John Smith"
        }
        self.assertEqual(resolve_form_type(form_data), "ICS-213")
        
        # Test with form ID
        form_data = {
            "to": "Jane Doe",
            "from": "John Smith"
        }
        self.assertEqual(resolve_form_type(form_data, form_id="ICS213-123"), "ICS-213")
        
        # Test with content signature
        form_data = {
            "to": "Jane Doe",
            "from": "John Smith",
            "subject": "Test Message",
            "message": "This is a test message"
        }
        self.assertEqual(resolve_form_type(form_data), "ICS-213")
        
        # Test with activity log (ICS-214)
        form_data = {
            "activity_log": [
                {"time": "10:00", "activity": "Test activity"}
            ],
            "prepared_by": "John Smith"
        }
        self.assertEqual(resolve_form_type(form_data), "ICS-214")
        
        # Test with malformed data
        form_data = {
            "random_field": "Random value"
        }
        # Should fall back to default
        self.assertEqual(resolve_form_type(form_data), "ICS-213")
        
        # Test with ambiguous data
        form_data = {
            "name": "John Smith",
            "title": "Test Form"
        }
        # Should fall back to default
        self.assertEqual(resolve_form_type(form_data), "ICS-213")
        
        # Test with alternative field names
        form_data = {
            "sender": "John Smith",
            "recipient": "Jane Doe",
            "message_body": "This is a test message"
        }
        self.assertEqual(resolve_form_type(form_data), "ICS-213")
    
    def test_ics213_full_workflow(self):
        """
        Test a complete ICS-213 form workflow using outcome-based testing.
        """
        # Create workflow tester
        workflow_tester = FormWorkflowTester(self)
        
        # Define initial and updated data
        initial_data = {
            "to": "Jane Doe",
            "from": "John Smith",
            "subject": "Test Message",
            "message": "Initial message",
            "date": datetime.date.today().isoformat(),
            "time": "10:00"
        }
        
        updated_data = {
            "message": "Updated message",
            "approved_by": "Supervisor"
        }
        
        # Test create-update workflow
        result = workflow_tester.test_create_update_workflow(
            form_type="ICS-213",
            initial_data=initial_data,
            updated_data=updated_data
        )
        
        # Get the form ID for further testing
        form_id = result["form_id"]
        
        # Test state transitions
        transition_result = workflow_tester.test_state_transition_workflow(
            form_type="ICS-213",
            initial_data={
                "to": "Operations Chief",
                "from": "Planning Chief",
                "subject": "Transition Test",
                "message": "Testing state transitions"
            },
            transitions=["approved", "transmitted", "received"]
        )
        
        # Verify final state
        self.assertEqual(transition_result["final_state"], "received")
        
        # Test form versioning
        version_data = [
            # Version 0 (initial)
            {
                "to": "Logistics Chief",
                "from": "Operations Chief",
                "subject": "Version Test",
                "message": "Initial version"
            },
            # Version 1 (first update)
            {
                "message": "Updated in version 1"
            },
            # Version 2 (second update)
            {
                "message": "Updated in version 2",
                "approved_by": "Commander"
            }
        ]
        
        version_result = workflow_tester.test_form_versioning_workflow(
            form_type="ICS-213",
            version_data=version_data
        )
        
        # Verify versions were created
        self.assertEqual(len(version_result["versions"]), 2)
        
        # Verify the content of the latest version
        current_form = version_result["current_form"]
        self.assertEqual(current_form.message, "Updated in version 2")
        self.assertEqual(current_form.approved_by, "Commander")
    
    def test_ics214_full_workflow(self):
        """
        Test a complete ICS-214 form workflow using outcome-based testing.
        """
        # Create workflow tester
        workflow_tester = FormWorkflowTester(self)
        
        # Define initial activity log
        initial_activities = [
            {
                "time": "08:00",
                "date": datetime.date.today().isoformat(),
                "activity": "Started shift"
            }
        ]
        
        # Define updated activity log
        updated_activities = [
            {
                "time": "08:00",
                "date": datetime.date.today().isoformat(),
                "activity": "Started shift"
            },
            {
                "time": "10:00",
                "date": datetime.date.today().isoformat(),
                "activity": "Coordinated response"
            }
        ]
        
        # Test create-update workflow
        result = workflow_tester.test_create_update_workflow(
            form_type="ICS-214",
            initial_data={
                "name": "John Smith",
                "position": "Operations Section Chief",
                "home_agency": "City Fire Department",
                "prepared_by": "John Smith",
                "activity_log": initial_activities,
                "date_from": datetime.date.today().isoformat(),
                "date_to": datetime.date.today().isoformat(),
                "time_from": "08:00",
                "time_to": "16:00"
            },
            updated_data={
                "activity_log": updated_activities
            }
        )
        
        # Verify the form was created and updated correctly
        form = result["form"]
        self.assertEqual(len(form.activity_log), 2)
        self.assertEqual(form.activity_log[1]["time"], "10:00")
        self.assertEqual(form.activity_log[1]["activity"], "Coordinated response")
    
    def test_form_loading_with_minimal_data(self):
        """
        Test form loading with minimal data to validate fallback mechanisms.
        """
        # Create a form with minimal data
        form_id = self.create_test_form(
            form_type="ICS-213",
            to="Jane Doe",
            from_field="John Smith",  # Using alternative field name
            subject="Minimal Data Test"
        )
        
        # Load the form
        form = self.form_registry.load_form(form_id)
        
        # Verify form was loaded correctly
        self.assertIsNotNone(form)
        self.assertEqual(form.form_id, form_id)
        self.assertEqual(form.to, "Jane Doe")
        self.assertEqual(form.from_field, "John Smith")  # Should handle the alternative field name
        
        # Create a form with no explicit type in the database
        conn = self.db_manager.connect()
        
        # Insert a form with minimal data and no explicit form_type
        form_id_2 = "MINIMAL-TEST-001"
        data = json.dumps({
            "to": "Operations",
            "from": "Planning",
            "message": "Test message"
        })
        
        conn.execute(
            """
            INSERT INTO forms (
                form_id, form_type, state, data, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (form_id_2, "", "draft", data, datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat())
        )
        conn.commit()
        
        # Load the form - should use form resolver to determine type
        form = self.form_registry.load_form(form_id_2)
        
        # Verify form was loaded correctly and type was resolved
        self.assertIsNotNone(form)
        self.assertEqual(form.form_id, form_id_2)
        # Should be resolved as ICS-213 based on fields
        self.assertIsInstance(form, EnhancedICS213Form)
    
    def test_database_schema_versioning(self):
        """
        Test database schema versioning functionality.
        """
        # Create a temporary database file
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_schema.db")
        
        # Import schema manager
        from radioforms.database.schema_manager import SchemaManager
        
        # Create schema manager
        schema_manager = SchemaManager(db_path)
        
        # Initialize schema
        self.assertTrue(schema_manager.initialize())
        
        # Verify current version is 0 (empty database)
        self.assertEqual(schema_manager.get_current_version(), 0)
        
        # Upgrade to latest version
        self.assertTrue(schema_manager.upgrade())
        
        # Verify new version
        current_version = schema_manager.get_current_version()
        self.assertGreater(current_version, 0)
        
        # Verify schema is valid
        is_valid, issues = schema_manager.verify_schema()
        self.assertTrue(is_valid, f"Schema validation failed: {issues}")
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


class TestFunctionalFormRegistry(FunctionalTestCase):
    """
    Tests for the form registry using real database and functional testing approach.
    """
    
    def test_form_registry_with_real_db(self):
        """
        Test form registry operations with a real database.
        """
        # Create and save a form
        form = self.form_registry.create_form("ICS-213")
        form.to = "Jane Doe"
        form.from_field = "John Smith"
        form.subject = "Test Subject"
        form.message = "Test message"
        
        form_id = self.form_registry.save_form(form)
        
        # Verify form was saved correctly
        self.assert_form_saved(form_id, expected_type="ICS-213")
        
        # Load the form
        loaded_form = self.form_registry.load_form(form_id)
        
        # Verify form was loaded correctly
        self.assert_form_loaded(loaded_form, form_id)
        self.assert_form_content(loaded_form, {
            "to": "Jane Doe",
            "from_field": "John Smith",
            "subject": "Test Subject",
            "message": "Test message"
        })
        
        # Find forms
        forms = self.form_registry.find_forms(form_type="ICS-213")
        
        # Verify forms were found
        self.assertGreater(len(forms), 0)
        found = False
        for form in forms:
            if form.form_id == form_id:
                found = True
                break
        self.assertTrue(found, f"Form with ID {form_id} not found in search results")
        
        # Delete the form
        self.form_registry.delete_form(form_id)
        
        # Verify form was deleted
        loaded_form = self.form_registry.load_form(form_id)
        self.assertIsNone(loaded_form)


if __name__ == '__main__':
    unittest.main()
