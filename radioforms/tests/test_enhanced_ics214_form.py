#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the Enhanced ICS-214 Activity Log form model.

This module contains tests for the EnhancedICS214Form class, focusing on
activity log entry management, personnel tracking, validation, and DAO integration.
"""

import unittest
import datetime
from unittest.mock import MagicMock, patch

from radioforms.models.enhanced_ics214_form import EnhancedICS214Form, FormState, ActivityLogEntry
from radioforms.models.base_form import ValidationResult


class TestActivityLogEntry(unittest.TestCase):
    """Test cases for the ActivityLogEntry class."""
    
    def test_initialization(self):
        """Test that an activity log entry is initialized with the correct defaults."""
        entry = ActivityLogEntry()
        
        # Check that entry_id was generated
        self.assertIsNotNone(entry.entry_id)
        
        # Check default values
        self.assertIsInstance(entry.time, datetime.time)
        self.assertEqual(entry.activity, "")
        self.assertFalse(entry.notable)
        
    def test_to_dict(self):
        """Test conversion to dictionary."""
        entry = ActivityLogEntry(
            time=datetime.time(14, 30),
            activity="Test activity",
            notable=True,
            entry_id="test-123"
        )
        
        entry_dict = entry.to_dict()
        
        self.assertEqual(entry_dict["entry_id"], "test-123")
        self.assertEqual(entry_dict["time"], "14:30:00")
        self.assertEqual(entry_dict["activity"], "Test activity")
        self.assertTrue(entry_dict["notable"])
        
    def test_from_dict(self):
        """Test creation from dictionary."""
        entry_dict = {
            "entry_id": "test-123",
            "time": "14:30:00",
            "activity": "Test activity",
            "notable": True
        }
        
        entry = ActivityLogEntry.from_dict(entry_dict)
        
        self.assertEqual(entry.entry_id, "test-123")
        self.assertEqual(entry.time, datetime.time(14, 30))
        self.assertEqual(entry.activity, "Test activity")
        self.assertTrue(entry.notable)
        
    def test_validation(self):
        """Test validation rules."""
        # Valid entry
        entry = ActivityLogEntry(
            time=datetime.time(14, 30),
            activity="Test activity"
        )
        
        result = entry.validate()
        self.assertTrue(result.is_valid)
        
        # Missing activity
        entry = ActivityLogEntry(
            time=datetime.time(14, 30),
            activity=""
        )
        
        result = entry.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("activity", result.errors)
        
        # Activity too long
        entry = ActivityLogEntry(
            time=datetime.time(14, 30),
            activity="X" * 501
        )
        
        result = entry.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("activity", result.errors)
        
        # Future time
        future_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).time()
        entry = ActivityLogEntry(
            time=future_time,
            activity="Test activity"
        )
        
        result = entry.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("time", result.errors)


class TestEnhancedICS214Form(unittest.TestCase):
    """Test cases for the enhanced ICS-214 form model."""
    
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.form = EnhancedICS214Form()
        
    def test_form_initialization(self):
        """Test that a new form is initialized with proper default values."""
        # Check initial state
        self.assertEqual(self.form.state, FormState.DRAFT)
        self.assertEqual(self.form.form_version, "2.0")
        
        # Check default dates
        now = datetime.datetime.now()
        self.assertAlmostEqual(self.form.date_prepared.timestamp(), now.timestamp(), delta=5)
        self.assertIsNone(self.form.reviewer_date)
        
        # Check empty collections
        self.assertEqual(len(self.form.activity_log), 0)
        self.assertEqual(len(self.form.personnel), 0)
        self.assertEqual(len(self.form.attachments), 0)
        
        # Check form type
        self.assertEqual(self.form.get_form_type(), "ICS-214")
        
    def test_form_properties(self):
        """Test form property getters and setters."""
        # Set properties
        self.form.incident_name = "Test Incident"
        self.form.incident_number = "INC-123"
        self.form.operational_period = "0700-1900"
        self.form.team_name = "Operations Team Alpha"
        self.form.ics_position = "Operations Section Chief"
        self.form.home_agency = "Agency XYZ"
        
        # Check properties
        self.assertEqual(self.form.incident_name, "Test Incident")
        self.assertEqual(self.form.incident_number, "INC-123")
        self.assertEqual(self.form.operational_period, "0700-1900")
        self.assertEqual(self.form.team_name, "Operations Team Alpha")
        self.assertEqual(self.form.ics_position, "Operations Section Chief")
        self.assertEqual(self.form.home_agency, "Agency XYZ")
        
    def test_activity_management(self):
        """Test adding, updating, and removing activities."""
        # Add an activity
        activity1 = self.form.add_activity(
            time=datetime.time(14, 30),
            activity="Initial briefing",
            notable=True
        )
        
        # Check that it was added
        self.assertEqual(len(self.form.activity_log), 1)
        self.assertEqual(self.form.activity_log[0].activity, "Initial briefing")
        self.assertTrue(self.form.activity_log[0].notable)
        
        # Add another activity
        activity2 = self.form.add_activity(
            time=datetime.time(15, 0),
            activity="Resource allocation"
        )
        
        # Check that both exist
        self.assertEqual(len(self.form.activity_log), 2)
        
        # Update an activity
        result = self.form.update_activity(
            entry_id=activity1.entry_id,
            activity="Updated initial briefing"
        )
        
        # Check that update was successful
        self.assertTrue(result)
        self.assertEqual(self.form.activity_log[0].activity, "Updated initial briefing")
        self.assertTrue(self.form.activity_log[0].notable)  # Should still be notable
        
        # Remove an activity
        result = self.form.remove_activity(activity2.entry_id)
        
        # Check that remove was successful
        self.assertTrue(result)
        self.assertEqual(len(self.form.activity_log), 1)
        
        # Get notable activities
        activity3 = self.form.add_activity(
            time=datetime.time(16, 0),
            activity="Emergency response",
            notable=True
        )
        
        notable = self.form.get_notable_activities()
        self.assertEqual(len(notable), 2)
        
        # Clear activities
        self.form.clear_activities()
        self.assertEqual(len(self.form.activity_log), 0)
        
    def test_personnel_management(self):
        """Test adding, updating, and removing personnel."""
        # Add personnel
        person1 = self.form.add_personnel(
            name="John Doe",
            position="Team Lead",
            agency="Agency XYZ"
        )
        
        # Check that it was added
        self.assertEqual(len(self.form.personnel), 1)
        self.assertEqual(self.form.personnel[0]["name"], "John Doe")
        
        # Add another person
        person2 = self.form.add_personnel(
            name="Jane Smith",
            position="Operations",
            agency="Agency ABC"
        )
        
        # Check that both exist
        self.assertEqual(len(self.form.personnel), 2)
        
        # Update a person
        result = self.form.update_personnel(
            index=0,
            position="Senior Team Lead"
        )
        
        # Check that update was successful
        self.assertTrue(result)
        self.assertEqual(self.form.personnel[0]["position"], "Senior Team Lead")
        self.assertEqual(self.form.personnel[0]["name"], "John Doe")  # Should remain unchanged
        
        # Remove a person
        result = self.form.remove_personnel(1)
        
        # Check that remove was successful
        self.assertTrue(result)
        self.assertEqual(len(self.form.personnel), 1)
        
        # Clear personnel
        self.form.clear_personnel()
        self.assertEqual(len(self.form.personnel), 0)
        
    def test_validation_required_fields(self):
        """Test validation of required fields."""
        # Empty form should fail validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        
        # Check for required field errors
        self.assertIn("incident_name", result.errors)
        self.assertIn("team_name", result.errors)
        
        # Fill required fields
        self.form.incident_name = "Test Incident"
        self.form.team_name = "Operations Team Alpha"
        
        # Should pass basic validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_validation_field_formats(self):
        """Test validation of field formats."""
        # Fill required fields
        self.form.incident_name = "Test Incident"
        self.form.team_name = "Operations Team Alpha"
        self.form.prepared_name = "John123"  # Invalid name
        
        # Should fail format validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("prepared_name", result.errors)
        
        # Fix the invalid field
        self.form.prepared_name = "John Doe"
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_validation_field_lengths(self):
        """Test validation of field lengths."""
        # Fill required fields with valid values
        self.form.incident_name = "Test Incident"
        self.form.team_name = "Operations Team Alpha"
        
        # Add an overlength field
        self.form.incident_number = "X" * 51  # Exceeds 50 char limit
        
        # Should fail length validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("incident_number", result.errors)
        
        # Fix the invalid field
        self.form.incident_number = "INC-123"
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_validation_date_fields(self):
        """Test validation of date fields."""
        # Fill required fields with valid values
        self.form.incident_name = "Test Incident"
        self.form.team_name = "Operations Team Alpha"
        
        # Set future date
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        self.form.date_prepared = tomorrow
        
        # Should fail date validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("date_prepared", result.errors)
        
        # Fix the invalid field
        self.form.date_prepared = datetime.datetime.now()
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_validation_activity_entries(self):
        """Test validation of activity log entries."""
        # Fill required fields with valid values
        self.form.incident_name = "Test Incident"
        self.form.team_name = "Operations Team Alpha"
        
        # Add an activity with empty description
        self.form.add_activity(activity="")
        
        # Should fail validation due to activity entry
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("activity_log" in key for key in result.errors.keys()))
        
        # Clear invalid activities and add a valid one
        self.form.clear_activities()
        self.form.add_activity(activity="Valid activity")
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_state_transition_finalize(self):
        """Test form state transition: finalize."""
        # Set up a valid form
        self.form.incident_name = "Test Incident"
        self.form.team_name = "Operations Team Alpha"
        
        # Test finalization
        result = self.form.finalize("John Doe", "Operations Chief", "JDoe")
        self.assertTrue(result)
        self.assertEqual(self.form.state, FormState.FINALIZED)
        self.assertEqual(self.form.prepared_name, "John Doe")
        self.assertEqual(self.form.prepared_position, "Operations Chief")
        self.assertEqual(self.form.prepared_signature, "JDoe")
        
        # Cannot finalize an already finalized form
        result = self.form.finalize("Another Person", "Another Position", "AP")
        self.assertFalse(result)
        self.assertEqual(self.form.prepared_name, "John Doe")  # Unchanged
        
    def test_state_transition_review(self):
        """Test form state transition: review."""
        # Set up a valid form
        self.form.incident_name = "Test Incident"
        self.form.team_name = "Operations Team Alpha"
        
        # Cannot review a draft form
        result = self.form.review("Jane Smith", "Planning Chief", "JSmith")
        self.assertFalse(result)
        
        # Finalize the form first
        self.form.finalize("John Doe", "Operations Chief", "JDoe")
        
        # Now review the form
        result = self.form.review("Jane Smith", "Planning Chief", "JSmith")
        self.assertTrue(result)
        self.assertEqual(self.form.state, FormState.REVIEWED)
        self.assertEqual(self.form.reviewer_name, "Jane Smith")
        self.assertEqual(self.form.reviewer_position, "Planning Chief")
        self.assertEqual(self.form.reviewer_signature, "JSmith")
        
    def test_state_transition_archive(self):
        """Test form state transition: archive."""
        # Archive from any state
        result = self.form.archive()
        self.assertTrue(result)
        self.assertEqual(self.form.state, FormState.ARCHIVED)
        
        # Cannot archive an already archived form
        result = self.form.archive()
        self.assertFalse(result)
        
    def test_bulk_operations(self):
        """Test bulk operations for activities and personnel."""
        # Bulk add activities
        activities = [
            {"time": datetime.time(8, 0), "activity": "Morning briefing", "notable": True},
            {"time": datetime.time(10, 0), "activity": "Resource deployment"},
            {"time": datetime.time(12, 0), "activity": "Situation assessment"}
        ]
        
        result = self.form.bulk_add_activities(activities)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(self.form.activity_log), 3)
        
        # Bulk add personnel
        personnel = [
            {"name": "John Doe", "position": "Team Lead", "agency": "Agency A"},
            {"name": "Jane Smith", "position": "Operations", "agency": "Agency B"},
            {"name": "Bob Johnson", "position": "Logistics", "agency": "Agency C"}
        ]
        
        result = self.form.bulk_add_personnel(personnel)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(self.form.personnel), 3)
        
    def test_time_range_activities(self):
        """Test getting activities within a time range."""
        # Add activities at different times
        self.form.add_activity(time=datetime.time(8, 0), activity="Morning briefing")
        self.form.add_activity(time=datetime.time(10, 0), activity="Resource deployment")
        self.form.add_activity(time=datetime.time(12, 0), activity="Lunch break")
        self.form.add_activity(time=datetime.time(14, 0), activity="Afternoon briefing")
        self.form.add_activity(time=datetime.time(16, 0), activity="End of shift")
        
        # Get activities within morning hours
        morning_activities = self.form.get_activities_by_timerange(
            datetime.time(8, 0),
            datetime.time(12, 0)
        )
        
        self.assertEqual(len(morning_activities), 3)
        
        # Get activities within afternoon hours
        afternoon_activities = self.form.get_activities_by_timerange(
            datetime.time(12, 1),
            datetime.time(16, 0)
        )
        
        self.assertEqual(len(afternoon_activities), 2)
        
    def test_serialization(self):
        """Test serialization to and from dictionary."""
        # Set up a form with data
        self.form.incident_name = "Test Incident"
        self.form.incident_number = "INC-123"
        self.form.team_name = "Operations Team Alpha"
        self.form.ics_position = "Operations Section Chief"
        self.form.operational_period = "0700-1900"
        
        # Add activities
        self.form.add_activity(time=datetime.time(8, 0), activity="Morning briefing", notable=True)
        self.form.add_activity(time=datetime.time(12, 0), activity="Situation update")
        
        # Add personnel
        self.form.add_personnel("John Doe", "Team Lead", "Agency A")
        self.form.add_personnel("Jane Smith", "Operations", "Agency B")
        
        # Convert to dictionary
        form_dict = self.form.to_dict()
        
        # Check dictionary fields
        self.assertEqual(form_dict["incident_name"], "Test Incident")
        self.assertEqual(form_dict["incident_number"], "INC-123")
        self.assertEqual(form_dict["team_name"], "Operations Team Alpha")
        self.assertEqual(form_dict["ics_position"], "Operations Section Chief")
        self.assertEqual(form_dict["operational_period"], "0700-1900")
        self.assertEqual(len(form_dict["activity_log"]), 2)
        self.assertEqual(len(form_dict["personnel"]), 2)
        
        # Create a new form from the dictionary
        new_form = EnhancedICS214Form.from_dict(form_dict)
        
        # Check new form fields
        self.assertEqual(new_form.incident_name, "Test Incident")
        self.assertEqual(new_form.incident_number, "INC-123")
        self.assertEqual(new_form.team_name, "Operations Team Alpha")
        self.assertEqual(new_form.ics_position, "Operations Section Chief")
        self.assertEqual(new_form.operational_period, "0700-1900")
        self.assertEqual(len(new_form.activity_log), 2)
        self.assertEqual(new_form.activity_log[0].activity, "Morning briefing")
        self.assertTrue(new_form.activity_log[0].notable)
        self.assertEqual(len(new_form.personnel), 2)
        self.assertEqual(new_form.personnel[0]["name"], "John Doe")
        
    def test_dao_integration(self):
        """Test DAO integration methods."""
        # Create a mock FormDAO
        mock_dao = MagicMock()
        mock_dao.create.return_value = "123"
        mock_dao.find_by_id.return_value = {"id": "123", "incident_name": "Test Incident"}
        
        # Test create_with_dao
        form = EnhancedICS214Form.create_with_dao(mock_dao)
        self.assertEqual(form.form_id, "123")
        mock_dao.create.assert_called_once()
        
        # Test save_to_dao for a new form
        mock_dao.reset_mock()
        mock_dao.find_by_id.return_value = None
        mock_dao.create.return_value = "456"
        
        form = EnhancedICS214Form()
        form_id = form.save_to_dao(mock_dao)
        
        self.assertEqual(form_id, "456")
        self.assertEqual(form.form_id, "456")
        mock_dao.create.assert_called_once()
        
        # Test save_to_dao for an existing form
        mock_dao.reset_mock()
        mock_dao.find_by_id.return_value = {"id": "456", "incident_name": "Test Incident"}
        
        form.form_id = "456"
        form_id = form.save_to_dao(mock_dao)
        
        self.assertEqual(form_id, "456")
        mock_dao.update.assert_called_once()
        
        # Test load_from_dao
        mock_dao.reset_mock()
        mock_dao.find_by_id.return_value = {
            "form_id": "789",
            "form_type": "ICS-214",
            "incident_name": "Test Incident",
            "team_name": "Operations Team",
            "activity_log": [
                {"entry_id": "act1", "time": "08:00:00", "activity": "Morning briefing"}
            ],
            "personnel": [
                {"name": "John Doe", "position": "Team Lead", "agency": "Agency A"}
            ]
        }
        
        form = EnhancedICS214Form.load_from_dao(mock_dao, "789")
        
        self.assertIsNotNone(form)
        self.assertEqual(form.form_id, "789")
        self.assertEqual(form.incident_name, "Test Incident")
        self.assertEqual(form.team_name, "Operations Team")
        self.assertEqual(len(form.activity_log), 1)
        self.assertEqual(form.activity_log[0].activity, "Morning briefing")
        self.assertEqual(len(form.personnel), 1)
        self.assertEqual(form.personnel[0]["name"], "John Doe")
        
        mock_dao.find_by_id.assert_called_once_with("789")


if __name__ == '__main__':
    unittest.main()
