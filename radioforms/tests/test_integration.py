#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration tests for the RadioForms application.

These tests validate the interaction between different components 
of the application, ensuring they work together correctly.
"""

import os
import unittest
import tempfile
import json
import datetime
from pathlib import Path

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao import (
    UserDAO, IncidentDAO, FormDAO, AttachmentDAO, SettingDAO
)
from radioforms.database.models.user import User
from radioforms.database.models.incident import Incident
from radioforms.database.models.form import Form, FormStatus
from radioforms.database.models.form_version import FormVersion
from radioforms.database.models.attachment import Attachment
from radioforms.database.models.setting import Setting


class IntegrationTestCase(unittest.TestCase):
    """Integration test case for RadioForms application."""
    
    def setUp(self):
        """Set up a test environment."""
        # Create a temporary directory for the test
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
        
    def tearDown(self):
        """Clean up resources."""
        # Close the database connection
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_complete_workflow(self):
        """Test a complete workflow from user creation to form export."""
        # Step 1: Create a user
        user = User(name="Integration Test User", call_sign="TEST-INT")
        user_id = self.user_dao.create(user)
        self.assertIsNotNone(user_id)
        user.id = user_id
        
        # Step 2: Create an incident
        incident = Incident(
            name="Integration Test Incident",
            description="An incident for integration testing",
            start_date=datetime.datetime.now()
        )
        incident_id = self.incident_dao.create(incident)
        self.assertIsNotNone(incident_id)
        incident.id = incident_id
        
        # Step 3: Create a form with content
        form = Form(
            incident_id=incident.id,
            form_type="ICS-213",
            title="Integration Test Message",
            creator_id=user.id,
            status=FormStatus.DRAFT
        )
        
        form_content = {
            "to": "Incident Command",
            "from": "Planning Section",
            "subject": "Integration Test",
            "message": "This is a test message created during integration testing.",
            "date": datetime.datetime.now().isoformat()
        }
        
        form_id = self.form_dao.create_with_content(form, form_content, user.id)
        self.assertIsNotNone(form_id)
        form.id = form_id
        
        # Step 4: Create a test file attachment
        test_file_path = Path(self.temp_dir.name) / "test_attachment.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test attachment created during integration testing.")
            
        attachment = self.attachment_dao.create_from_file(
            form.id,
            str(test_file_path),
            "integration_test.txt",
            "text/plain"
        )
        self.assertIsNotNone(attachment.id)
        
        # Step 5: Update the form with new content
        updated_content = form_content.copy()
        updated_content["message"] = "This message has been updated during integration testing."
        
        self.assertTrue(self.form_dao.update_with_content(form, updated_content, user.id))
        
        # Step 6: Retrieve the form with its latest content
        retrieved_form, content = self.form_dao.get_with_content(form.id)
        self.assertEqual(retrieved_form.id, form.id)
        self.assertEqual(content["message"], updated_content["message"])
        
        # Step 7: Verify version history
        versions = self.form_dao.get_all_versions(form.id)
        self.assertEqual(len(versions), 2)  # Initial + update
        
        # Step 8: Verify attachment
        attachments = self.attachment_dao.find_by_form(form.id)
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].id, attachment.id)
        
        # Step 9: Finalize the form
        self.assertTrue(self.form_dao.update_status(form.id, FormStatus.FINALIZED))
        
        # Step 10: Verify the form status
        updated_form = self.form_dao.find_by_id(form.id)
        self.assertEqual(updated_form.status, FormStatus.FINALIZED)
        
        # Step 11: Save application settings
        self.setting_dao.set_value("user.last_login", user.id)
        self.setting_dao.set_value("incident.current", incident.id)
        self.setting_dao.set_value("form.recent", [form.id])
        
        # Step 12: Retrieve settings
        settings = self.setting_dao.get_settings_as_dict()
        self.assertEqual(len(settings), 3)
        self.assertEqual(settings["user.last_login"], user.id)
        self.assertEqual(settings["incident.current"], incident.id)
        self.assertEqual(settings["form.recent"], [form.id])
        
        # Step 13: Close the incident
        self.assertTrue(self.incident_dao.close_incident(incident.id))
        closed_incident = self.incident_dao.find_by_id(incident.id)
        self.assertFalse(closed_incident.is_active())
        
        # Step 14: Search for forms
        search_results = self.form_dao.search_forms("Integration Test")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].id, form.id)
        
    def test_cross_entity_references(self):
        """Test relationships between different entities."""
        # Create a user
        user = User(name="Reference Test User", call_sign="REF1")
        user.id = self.user_dao.create(user)
        
        # Create an incident
        incident = Incident(name="Reference Test Incident")
        incident.id = self.incident_dao.create(incident)
        
        # Create multiple forms for the incident
        form1 = Form(
            incident_id=incident.id,
            form_type="ICS-213",
            title="Form 1",
            creator_id=user.id
        )
        form1_content = {"message": "Form 1 content"}
        form1.id = self.form_dao.create_with_content(form1, form1_content, user.id)
        
        form2 = Form(
            incident_id=incident.id,
            form_type="ICS-214",
            title="Form 2",
            creator_id=user.id
        )
        form2_content = {"message": "Form 2 content"}
        form2.id = self.form_dao.create_with_content(form2, form2_content, user.id)
        
        # Create attachment for form1
        test_file_path = Path(self.temp_dir.name) / "ref_test.txt"
        with open(test_file_path, "w") as f:
            f.write("Reference test attachment content")
            
        attachment = self.attachment_dao.create_from_file(
            form1.id,
            str(test_file_path),
            "ref_test.txt",
            "text/plain"
        )
        
        # Test relationship: incident -> forms
        incident_forms = self.form_dao.find_by_incident(incident.id)
        self.assertEqual(len(incident_forms), 2)
        self.assertIn(form1.id, [f.id for f in incident_forms])
        self.assertIn(form2.id, [f.id for f in incident_forms])
        
        # Test relationship: user -> forms
        user_forms = self.form_dao.find_by_user(user.id)
        self.assertEqual(len(user_forms), 2)
        self.assertIn(form1.id, [f.id for f in user_forms])
        self.assertIn(form2.id, [f.id for f in user_forms])
        
        # Test relationship: form -> attachments
        form_attachments = self.attachment_dao.find_by_form(form1.id)
        self.assertEqual(len(form_attachments), 1)
        self.assertEqual(form_attachments[0].id, attachment.id)
        
        # Test deletion cascading (form deletion should remove attachments)
        self.form_dao.delete_with_versions(form1.id)
        
        # Verify form was deleted
        deleted_form = self.form_dao.find_by_id(form1.id)
        self.assertIsNone(deleted_form)
        
        # Verify attachment was deleted from database
        form_attachments = self.attachment_dao.find_by_form(form1.id)
        self.assertEqual(len(form_attachments), 0)
        
    def test_transaction_integrity(self):
        """Test database transaction integrity across multiple operations."""
        # Start a transaction
        with self.db_manager.transaction() as tx:
            # Create a user
            cursor = tx.execute(
                """
                INSERT INTO users (name, call_sign, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                ("Transaction User", "TX1", datetime.datetime.now(), datetime.datetime.now())
            )
            user_id = cursor.lastrowid
            
            # Create an incident
            cursor = tx.execute(
                """
                INSERT INTO incidents (name, description, start_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Transaction Incident", 
                    "Transaction test description",
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                    datetime.datetime.now()
                )
            )
            incident_id = cursor.lastrowid
            
            # Create a form
            cursor = tx.execute(
                """
                INSERT INTO forms (
                    incident_id, form_type, title, creator_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    "ICS-213",
                    "Transaction Form",
                    user_id,
                    str(FormStatus.DRAFT),
                    datetime.datetime.now(),
                    datetime.datetime.now()
                )
            )
            form_id = cursor.lastrowid
            
            # Create a form version
            tx.execute(
                """
                INSERT INTO form_versions (
                    form_id, version_number, content, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    form_id,
                    1,
                    json.dumps({"message": "Transaction content"}),
                    user_id,
                    datetime.datetime.now()
                )
            )
            
        # Verify all entities were created in a single transaction
        user = self.user_dao.find_by_call_sign("TX1")
        self.assertIsNotNone(user)
        
        incident = self.incident_dao.find_by_name("Transaction Incident")[0]
        self.assertIsNotNone(incident)
        
        form = self.form_dao.find_by_id(form_id)
        self.assertIsNotNone(form)
        
        # Verify form has a version
        form_with_content = self.form_dao.get_with_content(form_id)
        self.assertIsNotNone(form_with_content)
        self.assertEqual(form_with_content[1]["message"], "Transaction content")
        
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Create a user
        user = User(name="Error Recovery User", call_sign="ERR1")
        user.id = self.user_dao.create(user)
        
        # Create an incident
        incident = Incident(name="Error Recovery Incident")
        incident.id = self.incident_dao.create(incident)
        
        # Test transaction rollback on error
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
                        incident.id,
                        "ICS-213",
                        "Error Form",
                        user.id,
                        str(FormStatus.DRAFT),
                        datetime.datetime.now(),
                        datetime.datetime.now()
                    )
                )
                
                # This will fail - invalid SQL
                tx.execute("INSERT INTO invalid_table (col) VALUES (?)", (1,))
        except Exception:
            pass  # Expected to fail
            
        # Verify the transaction was rolled back
        forms = self.form_dao.find_by_incident(incident.id)
        self.assertEqual(len(forms), 0)  # No forms should have been created
        

if __name__ == "__main__":
    unittest.main()
