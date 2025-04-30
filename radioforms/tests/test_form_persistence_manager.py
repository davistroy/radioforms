#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the FormPersistenceManager.

This module contains tests for the FormPersistenceManager class which integrates
the form models with the DAO layer.
"""

import unittest
import os
import tempfile
from unittest.mock import MagicMock, patch

from radioforms.models.form_persistence_manager import FormPersistenceManager
from radioforms.models.enhanced_ics213_form import EnhancedICS213Form, FormState
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.database.dao.attachment_dao_refactored import AttachmentDAO


class TestFormPersistenceManager(unittest.TestCase):
    """Test cases for the FormPersistenceManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.form_dao = MagicMock(spec=FormDAO)
        self.attachment_dao = MagicMock(spec=AttachmentDAO)
        self.manager = FormPersistenceManager(self.form_dao, self.attachment_dao)
        
    def test_create_form(self):
        """Test creating a new form."""
        # Setup the mock
        self.form_dao.create.return_value = "123"
        
        # Create a form
        form = self.manager.create_form("ICS-213")
        
        # Verify the form was created
        self.assertIsNotNone(form)
        self.assertIsInstance(form, EnhancedICS213Form)
        self.assertEqual(form.form_id, "123")
        self.form_dao.create.assert_called_once()
        
        # Test creating an unsupported form type
        form = self.manager.create_form("UNSUPPORTED-TYPE")
        self.assertIsNone(form)
        
    def test_save_form(self):
        """Test saving a form."""
        # Create a form to save
        form = EnhancedICS213Form()
        form.to = "John Doe"
        form.from_field = "Jane Smith"
        form.subject = "Test Subject"
        
        # Test saving a new form
        self.form_dao.find_by_id.return_value = None
        self.form_dao.create.return_value = "456"
        
        form_id = self.manager.save_form(form)
        
        self.assertEqual(form_id, "456")
        self.assertEqual(form.form_id, "456")
        self.form_dao.create.assert_called_once()
        
        # Test updating an existing form
        self.form_dao.reset_mock()
        self.form_dao.find_by_id.return_value = {"id": "456", "to": "John Doe"}
        
        form_id = self.manager.save_form(form)
        
        self.assertEqual(form_id, "456")
        self.form_dao.update.assert_called_once()
        
        # Test creating a version
        self.form_dao.reset_mock()
        self.form_dao.find_by_id.return_value = {"id": "456", "to": "John Doe"}
        self.form_dao.create_version = MagicMock()
        
        form_id = self.manager.save_form(form, create_version=True)
        
        self.assertEqual(form_id, "456")
        self.form_dao.update.assert_called_once()
        self.form_dao.create_version.assert_called_once()
        
    def test_load_form(self):
        """Test loading a form."""
        # Test loading a form
        self.form_dao.find_by_id.return_value = {
            "form_id": "789",
            "form_type": "ICS-213",
            "to": "John Doe",
            "from": "Jane Smith",
            "subject": "Test Subject"
        }
        
        form = self.manager.load_form("789")
        
        self.assertIsNotNone(form)
        self.assertIsInstance(form, EnhancedICS213Form)
        self.assertEqual(form.to, "John Doe")
        self.assertEqual(form.from_field, "Jane Smith")
        self.assertEqual(form.subject, "Test Subject")
        
        # Test loading a non-existent form
        self.form_dao.reset_mock()
        self.form_dao.find_by_id.return_value = None
        
        form = self.manager.load_form("999")
        
        self.assertIsNone(form)
        
        # Test loading a specific version
        self.form_dao.reset_mock()
        self.form_dao.find_version_by_id = MagicMock(return_value={
            "form_id": "789",
            "form_type": "ICS-213",
            "to": "John Doe (Version)",
            "version": 2
        })
        
        form = self.manager.load_form("789", version_id="v2")
        
        self.assertIsNotNone(form)
        self.assertEqual(form.to, "John Doe (Version)")
        self.form_dao.find_version_by_id.assert_called_once_with("v2")
        
    def test_delete_form(self):
        """Test deleting a form."""
        self.form_dao.delete.return_value = True
        
        result = self.manager.delete_form("123")
        
        self.assertTrue(result)
        self.form_dao.delete.assert_called_once_with("123")
        
    def test_get_form_versions(self):
        """Test getting form versions."""
        # Set up mock for form versions
        versions = [
            {"id": "v1", "form_id": "123", "version": 1},
            {"id": "v2", "form_id": "123", "version": 2}
        ]
        self.form_dao.find_versions_by_form_id = MagicMock(return_value=versions)
        
        # Test getting versions
        result = self.manager.get_form_versions("123")
        
        self.assertEqual(result, versions)
        self.form_dao.find_versions_by_form_id.assert_called_once_with("123")
        
        # Test when find_versions_by_form_id is not available
        delattr(self.form_dao, 'find_versions_by_form_id')
        
        result = self.manager.get_form_versions("123")
        
        self.assertEqual(result, [])
        
    def test_find_forms(self):
        """Test finding forms with criteria."""
        # Set up mock for find_by
        forms = [
            {"form_id": "123", "form_type": "ICS-213", "to": "John Doe"},
            {"form_id": "456", "form_type": "ICS-213", "to": "Jane Smith"}
        ]
        self.form_dao.find_by = MagicMock(return_value=forms)
        
        # Test finding forms with criteria
        criteria = {"to": "John Doe"}
        result = self.manager.find_forms(criteria, as_dict=True)
        
        self.assertEqual(result, forms)
        self.form_dao.find_by.assert_called_once_with(criteria, as_dict=True)
        
        # Test finding forms and converting to instances
        self.form_dao.reset_mock()
        result = self.manager.find_forms(criteria, as_dict=False)
        
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], EnhancedICS213Form)
        self.assertEqual(result[0].to, "John Doe")
        
        # Test when find_by is not available
        delattr(self.form_dao, 'find_by')
        self.form_dao.find_all = MagicMock(return_value=forms)
        
        result = self.manager.find_forms(criteria, as_dict=True)
        
        # Should filter results manually
        self.form_dao.find_all.assert_called_once_with(as_dict=True)
        
    def test_attachment_management(self):
        """Test attachment management."""
        # Create a test file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_path = temp_file.name
            
        try:
            # Set up form
            form = EnhancedICS213Form()
            form.form_id = "123"
            
            # Set up mock for attachment creation
            mock_attachment = MagicMock()
            mock_attachment.id = 456
            self.attachment_dao.create_from_file.return_value = mock_attachment
            
            # Test adding an attachment
            attachment_id = self.manager.add_attachment(form, temp_path)
            
            self.assertEqual(attachment_id, "456")
            self.attachment_dao.create_from_file.assert_called_once()
            self.assertIn("456", form.attachments)
            
            # Test getting attachments
            mock_attachment_info = {"id": 456, "file_name": "test.txt"}
            self.attachment_dao.find_attachment_info.return_value = mock_attachment_info
            
            attachments = self.manager.get_form_attachments(form)
            
            self.assertEqual(len(attachments), 1)
            self.assertEqual(attachments[0], mock_attachment_info)
            self.attachment_dao.find_attachment_info.assert_called_once_with(456)
            
            # Test removing an attachment
            self.attachment_dao.delete_with_file.return_value = True
            
            result = self.manager.remove_attachment(form, "456")
            
            self.assertTrue(result)
            self.assertNotIn("456", form.attachments)
            self.attachment_dao.delete_with_file.assert_called_once_with(456)
            
        finally:
            # Clean up test file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
