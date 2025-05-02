#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functional Test Utilities.

This module provides utilities for writing functional tests that verify outcomes
rather than implementation details. These utilities help tests be more robust
in the face of implementation changes.
"""

import inspect
import unittest
import sqlite3
import json
import tempfile
import os
import logging
from typing import Any, Dict, List, Optional, Callable, Type, Union, Tuple
from pathlib import Path

# Add parent directory to path to import RadioForms modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import required RadioForms modules
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.database.db_manager import DBManager
from radioforms.tests.fixtures.db_fixture import DatabaseFixtureContext


logger = logging.getLogger(__name__)


class FunctionalTestCase(unittest.TestCase):
    """
    Base class for functional tests.
    
    This class extends unittest.TestCase with additional utilities for
    implementing functional tests that focus on outcomes rather than
    implementation details.
    """
    
    def setUp(self):
        """
        Set up test case with real database fixture.
        """
        # Use a real database fixture with sample data
        self.db_fixture = DatabaseFixtureContext()
        self.db_manager = self.db_fixture.__enter__()
        
        # Create form model registry using real database
        self.form_registry = FormModelRegistry()
        self.form_registry.set_form_dao(self.db_manager)
        
        # Set up other resources as needed
        
    def tearDown(self):
        """
        Clean up test case.
        """
        # Clean up database fixture
        self.db_fixture.__exit__(None, None, None)
    
    def assert_form_content(self, form, expected_content: Dict[str, Any]):
        """
        Assert that a form contains the expected content.
        
        This is an outcome-based assertion that verifies the form content
        matches expectations, without being dependent on implementation details.
        
        Args:
            form: Form object to test
            expected_content: Dictionary of expected form content
        """
        # Check top-level attributes
        for key, expected_value in expected_content.items():
            if hasattr(form, key):
                actual_value = getattr(form, key)
                self.assertEqual(
                    actual_value, 
                    expected_value, 
                    f"Form attribute '{key}' does not match expected value"
                )
    
    def assert_database_contains(self, table: str, expected_row: Dict[str, Any]):
        """
        Assert that database table contains a row matching expected values.
        
        This is an outcome-based assertion that verifies the database contains
        the expected data, without being dependent on implementation details.
        
        Args:
            table: Table name to query
            expected_row: Dictionary of expected column values
        """
        # Build where clause
        where_clauses = []
        params = []
        
        for column, value in expected_row.items():
            where_clauses.append(f"{column} = ?")
            params.append(value)
        
        # Query database
        if where_clauses:
            query = f"SELECT * FROM {table} WHERE {' AND '.join(where_clauses)}"
            cursor = self.db_manager.connect().execute(query, params)
            row = cursor.fetchone()
            
            self.assertIsNotNone(
                row, 
                f"No row found in table '{table}' matching {expected_row}"
            )
    
    def assert_form_saved(self, form_id: str, expected_type: str = None, expected_state: str = None):
        """
        Assert that a form was saved to the database.
        
        This is an outcome-based assertion that verifies the form was saved
        correctly, without being dependent on implementation details.
        
        Args:
            form_id: Form ID to check
            expected_type: Optional expected form type
            expected_state: Optional expected form state
        """
        # Query database for form
        query = "SELECT * FROM forms WHERE form_id = ?"
        cursor = self.db_manager.connect().execute(query, (form_id,))
        row = cursor.fetchone()
        
        # Assert form exists
        self.assertIsNotNone(row, f"Form with ID '{form_id}' not found in database")
        
        # Assert form type if specified
        if expected_type is not None:
            self.assertEqual(
                row["form_type"], 
                expected_type, 
                f"Form type does not match expected value"
            )
        
        # Assert form state if specified
        if expected_state is not None:
            self.assertEqual(
                row["state"], 
                expected_state, 
                f"Form state does not match expected value"
            )
    
    def assert_form_loaded(self, form, expected_form_id: str):
        """
        Assert that a form was loaded correctly.
        
        This is an outcome-based assertion that verifies the form was loaded
        with the correct ID, without being dependent on implementation details.
        
        Args:
            form: Form object to test
            expected_form_id: Expected form ID
        """
        self.assertIsNotNone(form, "Form was not loaded")
        self.assertEqual(
            form.form_id, 
            expected_form_id, 
            f"Form ID does not match expected value"
        )
    
    def assert_workflow_outcome(self, workflow_result, expected_outcome: Dict[str, Any]):
        """
        Assert that a workflow produced the expected outcome.
        
        This is an outcome-based assertion that verifies the workflow result
        matches expectations, without being dependent on implementation details.
        
        Args:
            workflow_result: Result of workflow to test
            expected_outcome: Dictionary of expected outcome values
        """
        for key, expected_value in expected_outcome.items():
            if hasattr(workflow_result, key):
                actual_value = getattr(workflow_result, key)
                self.assertEqual(
                    actual_value, 
                    expected_value, 
                    f"Workflow outcome '{key}' does not match expected value"
                )
            elif isinstance(workflow_result, dict) and key in workflow_result:
                actual_value = workflow_result[key]
                self.assertEqual(
                    actual_value, 
                    expected_value, 
                    f"Workflow outcome '{key}' does not match expected value"
                )
    
    def create_test_form(self, form_type: str, **kwargs) -> str:
        """
        Create a test form.
        
        This is a utility method for creating test forms with the specified
        type and attributes.
        
        Args:
            form_type: Form type to create
            **kwargs: Additional form attributes
            
        Returns:
            Form ID of created form
        """
        # Create form with registry
        form = self.form_registry.create_form(form_type)
        
        # Set attributes
        for key, value in kwargs.items():
            if hasattr(form, key):
                setattr(form, key, value)
        
        # Save form
        form_id = self.form_registry.save_form(form)
        return form_id


class FormWorkflowTester:
    """
    Utility for testing form workflows.
    
    This class provides utilities for testing complete form workflows,
    focusing on outcomes rather than implementation details.
    """
    
    def __init__(self, test_case: FunctionalTestCase):
        """
        Initialize the workflow tester.
        
        Args:
            test_case: FunctionalTestCase instance
        """
        self.test_case = test_case
        self.db_manager = test_case.db_manager
        self.form_registry = test_case.form_registry
    
    def test_create_update_workflow(self, form_type: str, initial_data: Dict[str, Any], 
                                   updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a create-update workflow.
        
        This method tests a complete workflow of creating a form, updating it,
        and verifying the results at each step.
        
        Args:
            form_type: Form type to create
            initial_data: Initial form data
            updated_data: Updated form data
            
        Returns:
            Dictionary with workflow results
        """
        # Create and save form
        form = self.form_registry.create_form(form_type)
        
        # Set initial data
        for key, value in initial_data.items():
            if hasattr(form, key):
                setattr(form, key, value)
        
        # Save form
        form_id = self.form_registry.save_form(form)
        
        # Verify form was saved correctly
        self.test_case.assert_form_saved(form_id, expected_type=form_type)
        
        # Load form
        loaded_form = self.form_registry.load_form(form_id)
        
        # Verify form was loaded correctly
        self.test_case.assert_form_loaded(loaded_form, form_id)
        
        # Verify initial content
        self.test_case.assert_form_content(loaded_form, initial_data)
        
        # Update form
        for key, value in updated_data.items():
            if hasattr(loaded_form, key):
                setattr(loaded_form, key, value)
        
        # Save updated form
        self.form_registry.save_form(loaded_form)
        
        # Load form again
        reloaded_form = self.form_registry.load_form(form_id)
        
        # Verify updated content
        self.test_case.assert_form_content(reloaded_form, updated_data)
        
        # Return results
        return {
            "form_id": form_id,
            "form": reloaded_form
        }
    
    def test_state_transition_workflow(self, form_type: str, initial_data: Dict[str, Any],
                                      transitions: List[str]) -> Dict[str, Any]:
        """
        Test a state transition workflow.
        
        This method tests a complete workflow of creating a form and transitioning
        it through multiple states, verifying the results at each step.
        
        Args:
            form_type: Form type to create
            initial_data: Initial form data
            transitions: List of states to transition through
            
        Returns:
            Dictionary with workflow results
        """
        # Create and save form
        form = self.form_registry.create_form(form_type)
        
        # Set initial data
        for key, value in initial_data.items():
            if hasattr(form, key):
                setattr(form, key, value)
        
        # Save form
        form_id = self.form_registry.save_form(form)
        
        # Verify form was saved correctly
        self.test_case.assert_form_saved(form_id, expected_type=form_type, expected_state="draft")
        
        # Transition through states
        current_form = form
        current_state = "draft"
        
        for next_state in transitions:
            # Transition state
            success = current_form.transition_state(next_state)
            
            # Verify transition was successful
            self.test_case.assertTrue(
                success, 
                f"Failed to transition from {current_state} to {next_state}"
            )
            
            # Save form
            self.form_registry.save_form(current_form)
            
            # Verify form state was updated in database
            self.test_case.assert_form_saved(form_id, expected_state=next_state)
            
            # Load form again
            current_form = self.form_registry.load_form(form_id)
            
            # Verify form state was loaded correctly
            self.test_case.assertEqual(
                current_form.state, 
                next_state, 
                f"Loaded form state does not match expected value"
            )
            
            current_state = next_state
        
        # Return results
        return {
            "form_id": form_id,
            "form": current_form,
            "final_state": current_state
        }
    
    def test_form_versioning_workflow(self, form_type: str, version_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test a form versioning workflow.
        
        This method tests a complete workflow of creating a form and creating
        multiple versions, verifying the results at each step.
        
        Args:
            form_type: Form type to create
            version_data: List of dictionaries with version data
            
        Returns:
            Dictionary with workflow results
        """
        # Create and save form
        form = self.form_registry.create_form(form_type)
        
        # Set initial data (from first version)
        for key, value in version_data[0].items():
            if hasattr(form, key):
                setattr(form, key, value)
        
        # Save form
        form_id = self.form_registry.save_form(form)
        
        # Verify form was saved correctly
        self.test_case.assert_form_saved(form_id, expected_type=form_type)
        
        # Create and verify versions
        versions = []
        
        for i, data in enumerate(version_data[1:], start=1):
            # Load form
            current_form = self.form_registry.load_form(form_id)
            
            # Update form data
            for key, value in data.items():
                if hasattr(current_form, key):
                    setattr(current_form, key, value)
            
            # Save form (creates new version)
            self.form_registry.save_form(current_form)
            
            # Verify version in database
            query = """
                SELECT * FROM form_versions 
                WHERE form_id = ? AND version = ?
            """
            cursor = self.db_manager.connect().execute(query, (form_id, i))
            version_row = cursor.fetchone()
            
            self.test_case.assertIsNotNone(
                version_row, 
                f"Version {i} not found in database"
            )
            
            # Load version
            version_form = self.form_registry.load_form(form_id, version_id=version_row["version_id"])
            
            # Verify version content
            self.test_case.assertIsNotNone(
                version_form, 
                f"Failed to load version {i}"
            )
            
            # Add to versions list
            versions.append({
                "version_id": version_row["version_id"],
                "version": i,
                "form": version_form
            })
        
        # Return results
        return {
            "form_id": form_id,
            "versions": versions,
            "current_form": self.form_registry.load_form(form_id)
        }


def verify_outcome(result, expected_outcome: Dict[str, Any]) -> bool:
    """
    Verify a result matches expected outcome.
    
    This is a utility function for checking that a result matches
    expectations, without asserting (for use outside of test cases).
    
    Args:
        result: Result to check
        expected_outcome: Dictionary of expected outcome values
        
    Returns:
        True if outcome matches expectations, False otherwise
    """
    for key, expected_value in expected_outcome.items():
        if hasattr(result, key):
            actual_value = getattr(result, key)
            if actual_value != expected_value:
                return False
        elif isinstance(result, dict) and key in result:
            actual_value = result[key]
            if actual_value != expected_value:
                return False
    
    return True


# Example usage
if __name__ == "__main__":
    class ExampleTest(FunctionalTestCase):
        def test_ics213_workflow(self):
            # Create workflow tester
            workflow_tester = FormWorkflowTester(self)
            
            # Test create-update workflow
            result = workflow_tester.test_create_update_workflow(
                form_type="ICS-213",
                initial_data={
                    "to": "Jane Doe",
                    "from": "John Smith",
                    "subject": "Test Message",
                    "message": "Initial message"
                },
                updated_data={
                    "message": "Updated message"
                }
            )
            
            # Verify outcome
            self.assert_workflow_outcome(
                result,
                {
                    "form": {
                        "to": "Jane Doe",
                        "from": "John Smith",
                        "subject": "Test Message",
                        "message": "Updated message"
                    }
                }
            )
    
    # Run test
    unittest.main()
