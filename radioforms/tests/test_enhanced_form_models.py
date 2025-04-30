#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for enhanced form models.

This module contains tests for the enhanced ICS form models with improved
validation, DAO integration, and state tracking.
"""

import unittest
import datetime
from unittest.mock import MagicMock, patch

from radioforms.models.enhanced_ics213_form import EnhancedICS213Form, FormState
from radioforms.models.base_form import ValidationResult


class TestEnhancedICS213Form(unittest.TestCase):
    """Test cases for the enhanced ICS-213 form model."""
    
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.form = EnhancedICS213Form()
        
    def test_form_initialization(self):
        """Test that a new form is initialized with proper default values."""
        # Check initial state
        self.assertEqual(self.form.state, FormState.DRAFT)
        self.assertEqual(self.form.form_version, "2.0")
        
        # Check default dates
        now = datetime.datetime.now()
        self.assertAlmostEqual(self.form.message_date.timestamp(), now.timestamp(), delta=5)
        self.assertAlmostEqual(self.form.sender_date.timestamp(), now.timestamp(), delta=5)
        self.assertIsNone(self.form.recipient_date)
        
        # Check default tracking information
        self.assertEqual(self.form.priority, "Routine")
        self.assertEqual(self.form.transmission_method, "")
        self.assertEqual(self.form.attachments, [])
        
        # Check form type
        self.assertEqual(self.form.get_form_type(), "ICS-213")
        
    def test_form_properties(self):
        """Test form property getters and setters."""
        # Set properties
        self.form.to = "John Doe"
        self.form.to_position = "Operations Section Chief"
        self.form.from_field = "Jane Smith"
        self.form.from_position = "Planning Section Chief"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        
        # Check properties
        self.assertEqual(self.form.to, "John Doe")
        self.assertEqual(self.form.to_position, "Operations Section Chief")
        self.assertEqual(self.form.from_field, "Jane Smith")
        self.assertEqual(self.form.from_position, "Planning Section Chief")
        self.assertEqual(self.form.subject, "Resource Request")
        self.assertEqual(self.form.message, "We need additional supplies.")
        
    def test_validation_required_fields(self):
        """Test validation of required fields."""
        # Empty form should fail validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        
        # Check for required field errors
        self.assertIn("to", result.errors)
        self.assertIn("from", result.errors)
        self.assertIn("subject", result.errors)
        self.assertIn("message", result.errors)
        self.assertIn("sender_name", result.errors)
        
        # Fill required fields
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        self.form.sender_name = "Jane Smith"
        
        # Should pass basic validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_validation_field_formats(self):
        """Test validation of field formats."""
        # Fill required fields
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        self.form.sender_name = "Jane123" # Invalid name
        
        # Should fail format validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("sender_name", result.errors)
        
        # Fix the invalid field
        self.form.sender_name = "Jane Smith"
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_validation_field_lengths(self):
        """Test validation of field lengths."""
        # Fill required fields with valid values
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        self.form.sender_name = "Jane Smith"
        
        # Add an overlength field
        self.form.to = "X" * 101  # Exceeds 100 char limit
        
        # Should fail length validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("to", result.errors)
        
        # Fix the invalid field
        self.form.to = "John Doe"
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_validation_date_fields(self):
        """Test validation of date fields."""
        # Fill required fields with valid values
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        self.form.sender_name = "Jane Smith"
        
        # Set future date
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        self.form.message_date = tomorrow
        
        # Should fail date validation
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("message_date", result.errors)
        
        # Fix the invalid field
        self.form.message_date = datetime.datetime.now()
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_cross_field_validation(self):
        """Test cross-field validation rules."""
        # Fill required fields with valid values
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "URGENT: Request"
        self.form.message = ""  # Empty message
        self.form.sender_name = "Jane Smith"
        
        # Should fail cross-field validation (urgent subject with empty message)
        result = self.form.validate()
        self.assertFalse(result.is_valid)
        self.assertIn("message", result.errors)
        
        # Fix the invalid field
        self.form.message = "This is an urgent request."
        
        # Should pass validation now
        result = self.form.validate()
        self.assertTrue(result.is_valid)
        
    def test_state_transition_approve(self):
        """Test form state transition: approve."""
        # Set up a valid form
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        
        # Test approval
        result = self.form.approve("Jane Smith", "Planning Section Chief", "JSmith")
        self.assertTrue(result)
        self.assertEqual(self.form.state, FormState.APPROVED)
        self.assertEqual(self.form.sender_name, "Jane Smith")
        self.assertEqual(self.form.sender_position, "Planning Section Chief")
        self.assertEqual(self.form.sender_signature, "JSmith")
        
        # Cannot approve an already approved form
        result = self.form.approve("Another Person", "Another Position", "AP")
        self.assertFalse(result)
        self.assertEqual(self.form.sender_name, "Jane Smith")  # Unchanged
        
    def test_state_transition_transmit(self):
        """Test form state transition: transmit."""
        # Set up a valid form
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        
        # Transmit from DRAFT state
        result = self.form.transmit("Radio")
        self.assertTrue(result)
        self.assertEqual(self.form.state, FormState.TRANSMITTED)
        self.assertEqual(self.form.transmission_method, "Radio")
        
        # Cannot transmit an already transmitted form
        result = self.form.transmit("Email")
        self.assertFalse(result)
        self.assertEqual(self.form.transmission_method, "Radio")  # Unchanged
        
    def test_state_transition_receive(self):
        """Test form state transition: receive."""
        # Set up a valid form
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        
        # Cannot receive a draft form
        result = self.form.receive("John Doe", "Operations Section Chief")
        self.assertFalse(result)
        
        # Transmit the form first
        self.form.transmit("Radio")
        
        # Now receive the form
        result = self.form.receive("John Doe", "Operations Section Chief")
        self.assertTrue(result)
        self.assertEqual(self.form.state, FormState.RECEIVED)
        self.assertEqual(self.form.recipient_name, "John Doe")
        self.assertEqual(self.form.recipient_position, "Operations Section Chief")
        
    def test_state_transition_reply(self):
        """Test form state transition: reply."""
        # Set up a valid form
        self.form.to = "John Doe"
        self.form.from_field = "Jane Smith"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        
        # Cannot reply to a draft form
        result = self.form.reply_to_message("Request approved.", "JDoe")
        self.assertFalse(result)
        
        # Transmit and receive the form
        self.form.transmit("Radio")
        self.form.receive("John Doe", "Operations Section Chief")
        
        # Now reply to the form
        result = self.form.reply_to_message("Request approved.", "JDoe")
        self.assertTrue(result)
        self.assertEqual(self.form.state, FormState.REPLIED)
        self.assertEqual(self.form.reply, "Request approved.")
        self.assertEqual(self.form.recipient_signature, "JDoe")
        
    def test_attachment_management(self):
        """Test attachment management."""
        # Add an attachment
        result = self.form.add_attachment("attachment1")
        self.assertTrue(result)
        self.assertEqual(self.form.attachments, ["attachment1"])
        
        # Add another attachment
        result = self.form.add_attachment("attachment2")
        self.assertTrue(result)
        self.assertEqual(self.form.attachments, ["attachment1", "attachment2"])
        
        # Adding the same attachment again should fail
        result = self.form.add_attachment("attachment1")
        self.assertFalse(result)
        self.assertEqual(self.form.attachments, ["attachment1", "attachment2"])
        
        # Remove an attachment
        result = self.form.remove_attachment("attachment1")
        self.assertTrue(result)
        self.assertEqual(self.form.attachments, ["attachment2"])
        
        # Removing a non-existent attachment should fail
        result = self.form.remove_attachment("attachment3")
        self.assertFalse(result)
        self.assertEqual(self.form.attachments, ["attachment2"])
        
    def test_serialization(self):
        """Test serialization to and from dictionary."""
        # Set up a form with data
        self.form.to = "John Doe"
        self.form.to_position = "Operations Section Chief"
        self.form.from_field = "Jane Smith"
        self.form.from_position = "Planning Section Chief"
        self.form.subject = "Resource Request"
        self.form.message = "We need additional supplies."
        self.form.sender_name = "Jane Smith"
        self.form.sender_position = "Planning Section Chief"
        self.form.sender_signature = "JSmith"
        self.form.priority = "Priority"
        self.form.add_attachment("attachment1")
        
        # Convert to dictionary
        form_dict = self.form.to_dict()
        
        # Check dictionary fields
        self.assertEqual(form_dict["to"], "John Doe")
        self.assertEqual(form_dict["to_position"], "Operations Section Chief")
        self.assertEqual(form_dict["from"], "Jane Smith")
        self.assertEqual(form_dict["from_position"], "Planning Section Chief")
        self.assertEqual(form_dict["subject"], "Resource Request")
        self.assertEqual(form_dict["message"], "We need additional supplies.")
        self.assertEqual(form_dict["sender_name"], "Jane Smith")
        self.assertEqual(form_dict["sender_position"], "Planning Section Chief")
        self.assertEqual(form_dict["sender_signature"], "JSmith")
        self.assertEqual(form_dict["priority"], "Priority")
        self.assertEqual(form_dict["attachments"], ["attachment1"])
        
        # Create a new form from the dictionary
        new_form = EnhancedICS213Form.from_dict(form_dict)
        
        # Check new form fields
        self.assertEqual(new_form.to, "John Doe")
        self.assertEqual(new_form.to_position, "Operations Section Chief")
        self.assertEqual(new_form.from_field, "Jane Smith")
        self.assertEqual(new_form.from_position, "Planning Section Chief")
        self.assertEqual(new_form.subject, "Resource Request")
        self.assertEqual(new_form.message, "We need additional supplies.")
        self.assertEqual(new_form.sender_name, "Jane Smith")
        self.assertEqual(new_form.sender_position, "Planning Section Chief")
        self.assertEqual(new_form.sender_signature, "JSmith")
        self.assertEqual(new_form.priority, "Priority")
        self.assertEqual(new_form.attachments, ["attachment1"])
        
    def test_dao_integration(self):
        """Test DAO integration methods."""
        # Create a mock FormDAO
        mock_dao = MagicMock()
        mock_dao.create.return_value = "123"
        mock_dao.find_by_id.return_value = {"id": "123", "to": "John Doe"}
        
        # Test create_with_dao
        form = EnhancedICS213Form.create_with_dao(mock_dao)
        self.assertEqual(form.form_id, "123")
        mock_dao.create.assert_called_once()
        
        # Test save_to_dao for a new form
        mock_dao.reset_mock()
        mock_dao.find_by_id.return_value = None
        mock_dao.create.return_value = "456"
        
        form = EnhancedICS213Form()
        form_id = form.save_to_dao(mock_dao)
        
        self.assertEqual(form_id, "456")
        self.assertEqual(form.form_id, "456")
        mock_dao.create.assert_called_once()
        
        # Test save_to_dao for an existing form
        mock_dao.reset_mock()
        mock_dao.find_by_id.return_value = {"id": "456", "to": "John Doe"}
        
        form.form_id = "456"
        form_id = form.save_to_dao(mock_dao)
        
        self.assertEqual(form_id, "456")
        mock_dao.update.assert_called_once()
        
        # Test load_from_dao
        mock_dao.reset_mock()
        mock_dao.find_by_id.return_value = {
            "form_id": "789",
            "to": "John Doe",
            "from": "Jane Smith",
            "subject": "Test Subject",
            "message": "Test Message"
        }
        
        form = EnhancedICS213Form.load_from_dao(mock_dao, "789")
        
        self.assertIsNotNone(form)
        self.assertEqual(form.form_id, "789")
        self.assertEqual(form.to, "John Doe")
        self.assertEqual(form.from_field, "Jane Smith")
        self.assertEqual(form.subject, "Test Subject")
        self.assertEqual(form.message, "Test Message")
        
        mock_dao.find_by_id.assert_called_once_with("789")
        
        # Test load_from_dao with version_id
        mock_dao.reset_mock()
        mock_dao.find_version_by_id = MagicMock(return_value={
            "form_id": "789",
            "to": "John Doe (Version)",
            "version": 2
        })
        
        form = EnhancedICS213Form.load_from_dao(mock_dao, "789", version_id="v2")
        
        self.assertIsNotNone(form)
        self.assertEqual(form.to, "John Doe (Version)")
        mock_dao.find_version_by_id.assert_called_once_with("v2")


if __name__ == '__main__':
    unittest.main()
