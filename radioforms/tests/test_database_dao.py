#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the database data access objects (DAOs).
"""

import os
import unittest
import tempfile
import json
import datetime
from pathlib import Path

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao import (
    UserDAO, IncidentDAO, FormDAO, AttachmentDAO, SettingDAO, DAOException
)
from radioforms.database.models.user import User
from radioforms.database.models.incident import Incident
from radioforms.database.models.form import Form, FormStatus
from radioforms.database.models.form_version import FormVersion
from radioforms.database.models.attachment import Attachment
from radioforms.database.models.setting import Setting


class DAOTestCase(unittest.TestCase):
    """Test case for database DAO operations."""
    
    def setUp(self):
        """Set up a test database and DAOs."""
        # Create a temporary file for the test database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_radioforms.db"
        
        # Create a database manager instance
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create DAO instances
        self.user_dao = UserDAO(self.db_manager)
        self.incident_dao = IncidentDAO(self.db_manager)
        self.form_dao = FormDAO(self.db_manager)
        self.attachment_dao = AttachmentDAO(self.db_manager, self.temp_dir.name)
        self.setting_dao = SettingDAO(self.db_manager)
        
        # Create some test data
        self._create_test_data()
        
    def tearDown(self):
        """Clean up resources."""
        # Close the database connection
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def _create_test_data(self):
        """Create test data for all entities."""
        # Create a test user
        self.test_user = User(name="Test User", call_sign="TEST1")
        self.test_user.id = self.user_dao.create(self.test_user)
        
        # Create a test incident
        self.test_incident = Incident(
            name="Test Incident",
            description="A test incident for unit testing",
            start_date=datetime.datetime.now()
        )
        self.test_incident.id = self.incident_dao.create(self.test_incident)
        
        # Create a test form
        self.test_form = Form(
            incident_id=self.test_incident.id,
            form_type="ICS-213",
            title="Test Message Form",
            creator_id=self.test_user.id,
            status=FormStatus.DRAFT
        )
        
        # Create form with content
        test_content = {
            "to": "Command",
            "from": "Operations",
            "subject": "Test Message",
            "message": "This is a test message.",
            "date": datetime.datetime.now().isoformat()
        }
        self.test_form.id = self.form_dao.create_with_content(
            self.test_form, test_content, self.test_user.id
        )
        
        # Create a test setting
        self.test_setting = Setting(key="test.setting", value="test_value")
        self.test_setting.id = self.setting_dao.create(self.test_setting)
        
    def test_user_dao(self):
        """Test UserDAO operations."""
        # Test create (already done in setUp)
        self.assertIsNotNone(self.test_user.id)
        
        # Test find by ID
        user = self.user_dao.find_by_id(self.test_user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.call_sign, "TEST1")
        
        # Test find by call sign
        user = self.user_dao.find_by_call_sign("TEST1")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.test_user.id)
        
        # Test update
        user.name = "Updated User"
        self.assertTrue(self.user_dao.update(user))
        updated_user = self.user_dao.find_by_id(user.id)
        self.assertEqual(updated_user.name, "Updated User")
        
        # Test find by name
        users = self.user_dao.find_by_name("Updated")
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].id, self.test_user.id)
        
        # Test create if not exists
        new_user = self.user_dao.create_user_if_not_exists("New User", "NEW1")
        self.assertIsNotNone(new_user.id)
        found_user = self.user_dao.find_by_call_sign("NEW1")
        self.assertIsNotNone(found_user)
        
        # Test update_last_login
        self.assertTrue(self.user_dao.update_last_login(user.id))
        updated_user = self.user_dao.find_by_id(user.id)
        self.assertIsNotNone(updated_user.last_login)
        
    def test_incident_dao(self):
        """Test IncidentDAO operations."""
        # Test create (already done in setUp)
        self.assertIsNotNone(self.test_incident.id)
        
        # Test find by ID
        incident = self.incident_dao.find_by_id(self.test_incident.id)
        self.assertIsNotNone(incident)
        self.assertEqual(incident.name, "Test Incident")
        
        # Test find by name
        incidents = self.incident_dao.find_by_name("Test")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].id, self.test_incident.id)
        
        # Test update
        incident.description = "Updated description"
        self.assertTrue(self.incident_dao.update(incident))
        updated_incident = self.incident_dao.find_by_id(incident.id)
        self.assertEqual(updated_incident.description, "Updated description")
        
        # Test find active incidents
        active_incidents = self.incident_dao.find_active_incidents()
        self.assertEqual(len(active_incidents), 1)
        
        # Test close incident
        self.assertTrue(self.incident_dao.close_incident(incident.id))
        updated_incident = self.incident_dao.find_by_id(incident.id)
        self.assertFalse(updated_incident.is_active())
        
        # Test reopen incident
        self.assertTrue(self.incident_dao.reopen_incident(incident.id))
        updated_incident = self.incident_dao.find_by_id(incident.id)
        self.assertTrue(updated_incident.is_active())
        
        # Test incident stats
        stats = self.incident_dao.get_incident_stats()
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['active'], 1)
        self.assertEqual(stats['closed'], 0)
        
    def test_form_dao(self):
        """Test FormDAO operations."""
        # Test create with content (already done in setUp)
        self.assertIsNotNone(self.test_form.id)
        
        # Test find by ID
        form = self.form_dao.find_by_id(self.test_form.id)
        self.assertIsNotNone(form)
        self.assertEqual(form.title, "Test Message Form")
        
        # Test find with content
        form_with_content = self.form_dao.find_with_content(self.test_form.id)
        self.assertIsNotNone(form_with_content)
        self.assertIsInstance(form_with_content, tuple)
        self.assertEqual(len(form_with_content), 2)
        self.assertEqual(form_with_content[0].id, self.test_form.id)
        self.assertIsInstance(form_with_content[1], dict)
        self.assertEqual(form_with_content[1]["to"], "Command")
        
        # Test find with content as dict
        form_with_content_dict = self.form_dao.find_with_content(self.test_form.id, as_dict=True)
        self.assertIsNotNone(form_with_content_dict)
        self.assertIsInstance(form_with_content_dict, tuple)
        self.assertEqual(len(form_with_content_dict), 2)
        self.assertIsInstance(form_with_content_dict[0], dict)
        self.assertEqual(form_with_content_dict[0]["id"], self.test_form.id)
        self.assertEqual(form_with_content_dict[1]["to"], "Command")
        
        # Test update with content
        updated_content = {
            "to": "Updated Command",
            "from": "Operations",
            "subject": "Updated Test Message",
            "message": "This is an updated test message.",
            "date": datetime.datetime.now().isoformat()
        }
        form = form_with_content[0]
        form.title = "Updated Message Form"
        self.assertTrue(self.form_dao.update_with_content(form, updated_content, self.test_user.id))
        
        # Verify update
        updated_form = self.form_dao.find_with_content(form.id)
        self.assertEqual(updated_form[0].title, "Updated Message Form")
        self.assertEqual(updated_form[1]["to"], "Updated Command")
        
        # Test get all versions
        versions = self.form_dao.find_all_versions(form.id)
        self.assertEqual(len(versions), 2)  # Initial + update
        
        # Test find by incident
        forms = self.form_dao.find_by_incident(self.test_incident.id)
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0].id, self.test_form.id)
        
        # Test find by user
        forms = self.form_dao.find_by_user(self.test_user.id)
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0].id, self.test_form.id)
        
        # Test find by type
        forms = self.form_dao.find_by_type("ICS-213")
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0].id, self.test_form.id)
        
        # Test update status
        self.assertTrue(self.form_dao.update_status(form.id, FormStatus.FINALIZED))
        updated_form = self.form_dao.find_by_id(form.id)
        self.assertEqual(updated_form.status, FormStatus.FINALIZED)
        
        # Test search forms
        search_results = self.form_dao.search_forms("Updated")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].id, self.test_form.id)
        
    def test_attachment_dao(self):
        """Test AttachmentDAO operations."""
        # Create a temporary file for testing
        test_file_path = Path(self.temp_dir.name) / "test_file.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test file for attachment testing.")
            
        # Test create from file
        attachment = self.attachment_dao.create_from_file(
            self.test_form.id, 
            str(test_file_path), 
            "test_document.txt", 
            "text/plain"
        )
        self.assertIsNotNone(attachment)
        self.assertIsNotNone(attachment.id)
        
        # Test find by ID
        found_attachment = self.attachment_dao.find_by_id(attachment.id)
        self.assertIsNotNone(found_attachment)
        self.assertEqual(found_attachment.file_name, "test_document.txt")
        
        # Test find by form
        attachments = self.attachment_dao.find_by_form(self.test_form.id)
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].id, attachment.id)
        
        # Test get attachment info
        info = self.attachment_dao.get_attachment_info(attachment.id)
        self.assertIsNotNone(info)
        self.assertEqual(info["file_name"], "test_document.txt")
        self.assertTrue(info["exists"])
        
        # Test delete with file
        self.assertTrue(self.attachment_dao.delete_with_file(attachment.id))
        
        # Verify deletion
        deleted_attachment = self.attachment_dao.find_by_id(attachment.id)
        self.assertIsNone(deleted_attachment)
        
    def test_setting_dao(self):
        """Test SettingDAO operations."""
        # Test create (already done in setUp)
        self.assertIsNotNone(self.test_setting.id)
        
        # Test find by ID
        setting = self.setting_dao.find_by_id(self.test_setting.id)
        self.assertIsNotNone(setting)
        self.assertEqual(setting.key, "test.setting")
        
        # Test find by key
        setting = self.setting_dao.find_by_key("test.setting")
        self.assertIsNotNone(setting)
        self.assertEqual(setting.key, "test.setting")
        self.assertEqual(setting.value, "test_value")
        
        # Test find by key with as_dict
        setting_dict = self.setting_dao.find_by_key("test.setting", as_dict=True)
        self.assertIsNotNone(setting_dict)
        self.assertIsInstance(setting_dict, dict)
        self.assertEqual(setting_dict["key"], "test.setting")
        self.assertEqual(setting_dict["value"], "test_value")
        
        # Test get value
        value = self.setting_dao.get_value("test.setting")
        self.assertEqual(value, "test_value")
        
        # Test get value with default
        value = self.setting_dao.get_value("nonexistent.setting", "default_value")
        self.assertEqual(value, "default_value")
        
        # Test set value (update)
        updated_setting = self.setting_dao.set_value("test.setting", "updated_value")
        self.assertEqual(updated_setting.value, "updated_value")
        
        # Verify update
        setting = self.setting_dao.find_by_key("test.setting")
        self.assertEqual(setting.value, "updated_value")
        
        # Test set value (create new)
        new_setting = self.setting_dao.set_value("new.setting", 42)
        self.assertIsNotNone(new_setting.id)
        
        # Verify creation
        setting = self.setting_dao.find_by_key("new.setting")
        self.assertIsNotNone(setting)
        self.assertEqual(setting.value, 42)
        
        # Test get settings by prefix
        settings = self.setting_dao.get_settings_by_prefix("test")
        self.assertEqual(len(settings), 1)
        self.assertEqual(settings[0].key, "test.setting")
        
        # Test get settings as dict
        settings_dict = self.setting_dao.get_settings_as_dict()
        self.assertEqual(len(settings_dict), 2)  # test.setting and new.setting
        self.assertEqual(settings_dict["test.setting"], "updated_value")
        self.assertEqual(settings_dict["new.setting"], 42)
        
        # Test bulk set values
        bulk_values = {
            "bulk.setting1": "value1",
            "bulk.setting2": "value2",
            "bulk.setting3": 123
        }
        count = self.setting_dao.bulk_set_values(bulk_values)
        self.assertEqual(count, 3)
        
        # Verify bulk set
        settings_dict = self.setting_dao.get_settings_as_dict("bulk")
        self.assertEqual(len(settings_dict), 3)
        self.assertEqual(settings_dict["bulk.setting1"], "value1")
        self.assertEqual(settings_dict["bulk.setting3"], 123)
        
        # Test delete by key
        self.assertTrue(self.setting_dao.delete_by_key("test.setting"))
        
        # Verify deletion
        setting = self.setting_dao.find_by_key("test.setting")
        self.assertIsNone(setting)
        
    def test_transaction_handling(self):
        """Test transaction handling across DAOs."""
        # Create a new form within a transaction
        with self.db_manager.transaction() as tx:
            # Create a new user
            user = User(name="Transaction User", call_sign="TX1")
            cursor = tx.execute(
                "INSERT INTO users (name, call_sign, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user.name, user.call_sign, datetime.datetime.now(), datetime.datetime.now())
            )
            user_id = cursor.lastrowid
            
            # Create a new incident
            incident = Incident(name="Transaction Incident")
            cursor = tx.execute(
                "INSERT INTO incidents (name, start_date, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (incident.name, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now())
            )
            incident_id = cursor.lastrowid
            
            # Create a new form
            cursor = tx.execute(
                """
                INSERT INTO forms (
                    incident_id, form_type, title, creator_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id, "ICS-214", "Transaction Test Form", 
                    user_id, str(FormStatus.DRAFT),
                    datetime.datetime.now(), datetime.datetime.now()
                )
            )
            form_id = cursor.lastrowid
            
        # Verify all entities were created
        user = self.user_dao.find_by_call_sign("TX1")
        self.assertIsNotNone(user)
        
        incident = self.incident_dao.find_by_name("Transaction")
        self.assertEqual(len(incident), 1)
        
        form = self.form_dao.find_by_id(form_id)
        self.assertIsNotNone(form)
        self.assertEqual(form.title, "Transaction Test Form")
        
    def test_rollback_handling(self):
        """Test transaction rollback when an error occurs."""
        # Count forms before
        query = "SELECT COUNT(*) FROM forms"
        cursor = self.db_manager.execute(query)
        form_count_before = cursor.fetchone()[0]
        
        # Attempt a transaction that will fail
        try:
            with self.db_manager.transaction() as tx:
                # This will succeed
                tx.execute(
                    """
                    INSERT INTO forms (
                        incident_id, form_type, title, creator_id, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.test_incident.id, "ICS-215", "Rollback Test Form", 
                        self.test_user.id, str(FormStatus.DRAFT),
                        datetime.datetime.now(), datetime.datetime.now()
                    )
                )
                
                # This will fail (non-existent table)
                tx.execute(
                    "INSERT INTO nonexistent_table (name) VALUES (?)",
                    ("This will fail",)
                )
        except Exception:
            pass  # We expect this to fail
            
        # Count forms after
        cursor = self.db_manager.execute(query)
        form_count_after = cursor.fetchone()[0]
        
        # Verify no forms were added
        self.assertEqual(form_count_before, form_count_after)


if __name__ == "__main__":
    unittest.main()
