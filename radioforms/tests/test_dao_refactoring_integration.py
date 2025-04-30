#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration tests for refactored DAO classes.

This module contains tests that verify the refactored DAO classes work together
correctly in integrated scenarios that span multiple entity types.
"""

import os
import tempfile
import unittest
import json
from datetime import datetime, timedelta

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.incident_dao import IncidentDAO
from radioforms.database.dao.user_dao import UserDAO
from radioforms.database.dao.form_dao import FormDAO
from radioforms.database.dao.attachment_dao import AttachmentDAO
from radioforms.database.dao.setting_dao import SettingDAO

from radioforms.database.models.incident import Incident
from radioforms.database.models.user import User
from radioforms.database.models.form import Form, FormStatus
from radioforms.database.models.attachment import Attachment
from radioforms.database.models.setting import Setting


class DAORefactoringIntegrationTests(unittest.TestCase):
    """
    Integration tests for the refactored DAO implementations.
    
    These tests verify that refactored DAOs maintain correct behavior 
    when used together in complex operations spanning multiple entity types.
    """
    
    def setUp(self):
        """Set up a test database and DAO instances."""
        # Create a temporary database file
        fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create temporary directory for attachments
        self.attachment_dir = tempfile.mkdtemp(prefix='test_attachments_')
        
        # Create database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create DAO instances
        self.incident_dao = IncidentDAO(self.db_manager)
        self.user_dao = UserDAO(self.db_manager)
        self.form_dao = FormDAO(self.db_manager)
        self.attachment_dao = AttachmentDAO(self.db_manager, self.attachment_dir)
        self.setting_dao = SettingDAO(self.db_manager)
        
        # Create test schema
        self._create_test_schema()
        
        # Create test data files for attachments
        self.test_files = []
        for i in range(3):
            fd, file_path = tempfile.mkstemp(suffix=f'_test_{i}.txt')
            with os.fdopen(fd, 'w') as f:
                f.write(f"Test content for file {i}")
            self.test_files.append(file_path)
    
    def tearDown(self):
        """Clean up resources."""
        self.db_manager.close()
        
        # Remove temporary database file
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
            
        # Remove temporary attachment directory and contents
        if os.path.exists(self.attachment_dir):
            for root, dirs, files in os.walk(self.attachment_dir, topdown=False):
                for file in files:
                    os.unlink(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.attachment_dir)
            
        # Remove temporary test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def _create_test_schema(self):
        """Create test schema for all tables."""
        # Create incidents table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create users table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            call_sign TEXT UNIQUE,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create forms table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            form_type TEXT NOT NULL,
            title TEXT NOT NULL,
            creator_id INTEGER,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(id),
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
        ''')
        
        # Create form_versions table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS form_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            content TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES forms(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        ''')
        
        # Create attachments table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES forms(id)
        )
        ''')
        
        # Create settings table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    
    def test_create_incident_with_forms_and_attachments(self):
        """
        Test creating an incident with forms and attachments.
        
        This test verifies that multiple DAOs work together correctly when creating
        a complex structure with interdependent entities.
        """
        # 1. Create a user
        user = User(name="Test User", call_sign="W1XYZ")
        user_id = self.user_dao.create(user)
        self.assertIsNotNone(user_id)
        
        # 2. Create an incident
        incident = Incident(name="Test Incident", description="Integration test")
        incident_id = self.incident_dao.create(incident)
        self.assertIsNotNone(incident_id)
        
        # 3. Create a form linked to the incident and user
        form = Form(
            incident_id=incident_id,
            form_type="ICS-213",
            title="Test Message Form",
            creator_id=user_id,
            status=FormStatus.DRAFT
        )
        
        # Form content as a dictionary
        content = {
            "to": "Planning Section",
            "from": "Operations Section",
            "subject": "Integration Test",
            "message": "Testing integrated DAO operations",
            "approved_by": "Test User"
        }
        
        # Create form with content
        form_id = self.form_dao.create_with_content(form, content, user_id)
        self.assertIsNotNone(form_id)
        
        # 4. Add attachments to the form
        attachments = []
        for file_path in self.test_files:
            attachment = self.attachment_dao.create_from_file(form_id, file_path)
            attachments.append(attachment)
            self.assertIsNotNone(attachment.id)
        
        # 5. Store some settings
        settings = {
            "ui.theme": "dark",
            "ui.font_size": 14,
            f"incident.{incident_id}.last_accessed": datetime.now().isoformat()
        }
        settings_count = self.setting_dao.set_values_bulk(settings)
        self.assertEqual(settings_count, 3)
        
        # 6. Now verify the entire structure was created properly
        
        # Check incident retrieval
        retrieved_incident = self.incident_dao.find_by_id(incident_id)
        self.assertEqual(retrieved_incident.name, "Test Incident")
        
        # Check user retrieval
        retrieved_user = self.user_dao.find_by_id(user_id)
        self.assertEqual(retrieved_user.call_sign, "W1XYZ")
        
        # Check form with content retrieval
        retrieved_form_data = self.form_dao.find_with_content(form_id)
        self.assertIsNotNone(retrieved_form_data)
        
        retrieved_form, retrieved_content = retrieved_form_data
        self.assertEqual(retrieved_form.title, "Test Message Form")
        self.assertEqual(retrieved_content["message"], "Testing integrated DAO operations")
        
        # Check attachment retrieval
        form_attachments = self.attachment_dao.find_by_form(form_id)
        self.assertEqual(len(form_attachments), len(self.test_files))
        
        # Check settings retrieval
        theme = self.setting_dao.find_value("ui.theme")
        self.assertEqual(theme, "dark")
        
        # Get all settings as dictionary
        ui_settings = self.setting_dao.find_as_dict("ui.")
        self.assertEqual(len(ui_settings), 2)
        self.assertEqual(ui_settings["ui.font_size"], 14)
    
    def test_update_incident_cascade(self):
        """
        Test updating an incident and all its related entities.
        
        This test verifies that multiple DAOs work together correctly when updating
        a complex structure with interdependent entities.
        """
        # 1. First create the test data structure
        user = User(name="Test User", call_sign="W1XYZ")
        user_id = self.user_dao.create(user)
        
        incident = Incident(name="Original Incident", description="Original description")
        incident_id = self.incident_dao.create(incident)
        
        form = Form(
            incident_id=incident_id,
            form_type="ICS-213",
            title="Original Form",
            creator_id=user_id,
            status=FormStatus.DRAFT
        )
        content = {"message": "Original message"}
        form_id = self.form_dao.create_with_content(form, content, user_id)
        
        attachment = self.attachment_dao.create_from_file(form_id, self.test_files[0])
        
        # 2. Now update the incident
        # Fetch the incident first to ensure we have the ID
        incident = self.incident_dao.find_by_id(incident_id)
        incident.name = "Updated Incident"
        incident.description = "Updated description"
        update_success = self.incident_dao.update(incident)
        self.assertTrue(update_success)
        
        # 3. Update the form status
        form_status_updated = self.form_dao.set_form_status(form_id, FormStatus.FINALIZED)
        self.assertTrue(form_status_updated)
        
        # 4. Update the form content
        updated_form = self.form_dao.find_by_id(form_id)
        updated_content = {"message": "Updated message"}
        content_updated = self.form_dao.update_with_content(updated_form, updated_content, user_id)
        self.assertTrue(content_updated)
        
        # 5. Set user last login
        login_updated = self.user_dao.set_last_login_time(user_id)
        self.assertTrue(login_updated)
        
        # 6. Verify all updates were applied correctly
        
        # Check updated incident
        retrieved_incident = self.incident_dao.find_by_id(incident_id)
        self.assertEqual(retrieved_incident.name, "Updated Incident")
        self.assertEqual(retrieved_incident.description, "Updated description")
        
        # Check updated form
        retrieved_form_data = self.form_dao.find_with_content(form_id)
        self.assertIsNotNone(retrieved_form_data)
        
        retrieved_form, retrieved_content = retrieved_form_data
        self.assertEqual(str(retrieved_form.status), "finalized")
        self.assertEqual(retrieved_content["message"], "Updated message")
        
        # Check form versions
        versions = self.form_dao.find_versions(form_id)
        self.assertEqual(len(versions), 2)  # Original and updated
        
        # Check user login time was updated
        updated_user = self.user_dao.find_by_id(user_id)
        self.assertIsNotNone(updated_user.last_login)
    
    def test_cross_entity_operations(self):
        """
        Test operations that cross entity boundaries.
        
        This test verifies more complex operations that require coordination
        between multiple DAOs.
        """
        # Create initial data
        user1 = User(name="User One", call_sign="W1AAA")
        user2 = User(name="User Two", call_sign="W2BBB")
        user1_id = self.user_dao.create(user1)
        user2_id = self.user_dao.create(user2)
        
        incident1 = Incident(name="Incident One")
        incident2 = Incident(name="Incident Two")
        incident1_id = self.incident_dao.create(incident1)
        incident2_id = self.incident_dao.create(incident2)
        
        # Create forms in the first incident
        form1 = Form(incident_id=incident1_id, form_type="ICS-213", title="Form One", creator_id=user1_id)
        form2 = Form(incident_id=incident1_id, form_type="ICS-214", title="Form Two", creator_id=user1_id)
        form1_id = self.form_dao.create_with_content(form1, {"content": "Form 1"}, user1_id)
        form2_id = self.form_dao.create_with_content(form2, {"content": "Form 2"}, user1_id)
        
        # Add attachments to forms
        attachment1 = self.attachment_dao.create_from_file(form1_id, self.test_files[0])
        attachment2 = self.attachment_dao.create_from_file(form1_id, self.test_files[1])
        
        # Test 1: Find forms by incident
        incident1_forms = self.form_dao.find_by_incident(incident1_id)
        self.assertEqual(len(incident1_forms), 2)
        
        # Test 2: Find forms by user
        user1_forms = self.form_dao.find_by_user(user1_id)
        self.assertEqual(len(user1_forms), 2)
        
        # Test 3: Find forms with attachments
        form1_attachments = self.attachment_dao.find_by_form(form1_id)
        self.assertEqual(len(form1_attachments), 2)
        
        # Test 4: Cross-DAO operation - move a form to another incident
        # First, find the form
        form_to_move = self.form_dao.find_by_id(form1_id)
        # Update its incident_id
        form_to_move.incident_id = incident2_id
        # Update the form
        self.form_dao.update(form_to_move)
        
        # Verify the form is now associated with the second incident
        incident2_forms = self.form_dao.find_by_incident(incident2_id)
        self.assertEqual(len(incident2_forms), 1)
        self.assertEqual(incident2_forms[0].id, form1_id)
        
        # Test 5: Cross-DAO operation - move attachments to another form
        moved_count = self.attachment_dao.move_to_form(form1_id, form2_id)
        self.assertEqual(moved_count, 2)
        
        # Verify the attachments were moved
        form1_attachments_after = self.attachment_dao.find_by_form(form1_id)
        self.assertEqual(len(form1_attachments_after), 0)
        
        form2_attachments_after = self.attachment_dao.find_by_form(form2_id)
        self.assertEqual(len(form2_attachments_after), 2)
        
        # Test 6: Search across forms
        search_results = self.form_dao.search("Form")
        self.assertEqual(len(search_results), 2)
        
        # Test 7: Settings tied to entities
        self.setting_dao.set_value(f"incident.{incident1_id}.description", "Test description")
        self.setting_dao.set_value(f"user.{user1_id}.preferences.theme", "dark")
        
        # Retrieve by prefix
        incident_settings = self.setting_dao.find_by_prefix(f"incident.{incident1_id}.")
        self.assertEqual(len(incident_settings), 1)
        
        # Test 8: Advanced DAO operations - close an incident and check forms
        self.incident_dao.set_incident_closed(incident1_id)
        active_incidents = self.incident_dao.find_active()
        self.assertEqual(len(active_incidents), 1)  # Only incident2 is active
        
        # Test 9: Delete cascade operations
        # First verify that form2 has the attachments we moved to it
        form2_attachments = self.attachment_dao.find_by_form(form2_id)
        self.assertEqual(len(form2_attachments), 2)
        
        # Now delete the form and verify its attachments are removed
        self.form_dao.delete_cascade(form2_id)
        
        # Check if any attachments still exist for the deleted form
        deleted_form_attachments = self.attachment_dao.find_by_form(form2_id)
        self.assertEqual(len(deleted_form_attachments), 0)
        
        # Test 10: Find recent entities
        recent_forms = self.form_dao.find_recent(limit=5)
        # Only form1 should remain
        self.assertEqual(len(recent_forms), 1)
        
        # Test stats
        stats = self.incident_dao.find_incident_stats()
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['active'], 1)
        self.assertEqual(stats['closed'], 1)


if __name__ == '__main__':
    unittest.main()
