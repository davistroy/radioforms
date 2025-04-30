#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration tests for the refactored DAO layer.

This test suite specifically validates that the standardized BaseDAO interface
works correctly across all DAO implementations with both entity objects and dictionaries.
"""

import unittest
import tempfile
import datetime
from pathlib import Path

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao import (
    UserDAO, IncidentDAO, FormDAO, AttachmentDAO, SettingDAO
)
from radioforms.database.models.user import User
from radioforms.database.models.incident import Incident
from radioforms.database.models.form import Form, FormStatus
from radioforms.database.models.setting import Setting


class DAORefactoringTestCase(unittest.TestCase):
    """Test case for the refactored DAO implementations."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for the test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_dao_refactoring.db"
        
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
        
    def test_user_dao_entity_dict_interop(self):
        """Test UserDAO with both entity and dictionary operations."""
        # Create user with entity
        user_entity = User(
            name="Entity User",
            call_sign="ENT1"
        )
        user_entity_id = self.user_dao.create(user_entity)
        self.assertIsNotNone(user_entity_id)
        
        # Create user with dictionary
        user_dict = {
            "name": "Dict User",
            "call_sign": "DICT1"
        }
        user_dict_id = self.user_dao.create(user_dict)
        self.assertIsNotNone(user_dict_id)
        
        # Retrieve users in different formats
        # 1. Entity -> Entity
        entity_as_entity = self.user_dao.find_by_id(user_entity_id)
        self.assertIsInstance(entity_as_entity, User)
        self.assertEqual(entity_as_entity.name, "Entity User")
        
        # 2. Entity -> Dict
        entity_as_dict = self.user_dao.find_by_id(user_entity_id, as_dict=True)
        self.assertIsInstance(entity_as_dict, dict)
        self.assertEqual(entity_as_dict["name"], "Entity User")
        
        # 3. Dict -> Entity
        dict_as_entity = self.user_dao.find_by_id(user_dict_id)
        self.assertIsInstance(dict_as_entity, User)
        self.assertEqual(dict_as_entity.name, "Dict User")
        
        # 4. Dict -> Dict
        dict_as_dict = self.user_dao.find_by_id(user_dict_id, as_dict=True)
        self.assertIsInstance(dict_as_dict, dict)
        self.assertEqual(dict_as_dict["name"], "Dict User")
        
        # Test update with entity
        entity_as_entity.name = "Updated Entity User"
        self.assertTrue(self.user_dao.update(entity_as_entity))
        updated_entity = self.user_dao.find_by_id(entity_as_entity.id)
        self.assertEqual(updated_entity.name, "Updated Entity User")
        
        # Test update with dict
        dict_update = {"id": user_dict_id, "name": "Updated Dict User"}
        self.assertTrue(self.user_dao.update(dict_update))
        updated_dict_user = self.user_dao.find_by_id(user_dict_id)
        self.assertEqual(updated_dict_user.name, "Updated Dict User")
        
        # Test update with id and dict
        self.assertTrue(self.user_dao.update(user_entity_id, {"name": "Updated Again"}))
        updated_again = self.user_dao.find_by_id(user_entity_id)
        self.assertEqual(updated_again.name, "Updated Again")
        
    def test_incident_dao_entity_dict_interop(self):
        """Test IncidentDAO with both entity and dictionary operations."""
        # Create incident with entity
        incident_entity = Incident(
            name="Entity Incident",
            description="Test entity incident"
        )
        incident_entity_id = self.incident_dao.create(incident_entity)
        self.assertIsNotNone(incident_entity_id)
        
        # Create incident with dictionary
        incident_dict = {
            "name": "Dict Incident",
            "description": "Test dictionary incident",
            "start_date": datetime.datetime.now()
        }
        incident_dict_id = self.incident_dao.create(incident_dict)
        self.assertIsNotNone(incident_dict_id)
        
        # Retrieve incidents in different formats
        # 1. Entity -> Entity
        entity_as_entity = self.incident_dao.find_by_id(incident_entity_id)
        self.assertIsInstance(entity_as_entity, Incident)
        self.assertEqual(entity_as_entity.name, "Entity Incident")
        
        # 2. Entity -> Dict
        entity_as_dict = self.incident_dao.find_by_id(incident_entity_id, as_dict=True)
        self.assertIsInstance(entity_as_dict, dict)
        self.assertEqual(entity_as_dict["name"], "Entity Incident")
        
        # Test find by name with different return types
        incidents_as_entities = self.incident_dao.find_by_name("Incident")
        self.assertTrue(all(isinstance(inc, Incident) for inc in incidents_as_entities))
        self.assertEqual(len(incidents_as_entities), 2)
        
        incidents_as_dicts = self.incident_dao.find_by_name("Incident", as_dict=True)
        self.assertTrue(all(isinstance(inc, dict) for inc in incidents_as_dicts))
        self.assertEqual(len(incidents_as_dicts), 2)
        
        # Test find active incidents
        active_incidents = self.incident_dao.find_active_incidents()
        self.assertEqual(len(active_incidents), 2)  # Both are active by default
        
        # Close an incident and test filtering
        self.incident_dao.close_incident(incident_entity_id)
        active_incidents = self.incident_dao.find_active_incidents()
        self.assertEqual(len(active_incidents), 1)
        
        # Verify the incident was closed
        closed_incident = self.incident_dao.find_by_id(incident_entity_id)
        self.assertFalse(closed_incident.is_active())
        
        # Reopen and verify
        self.incident_dao.reopen_incident(incident_entity_id)
        reopened = self.incident_dao.find_by_id(incident_entity_id)
        self.assertTrue(reopened.is_active())
    
    def test_setting_dao_entity_dict_interop(self):
        """Test SettingDAO with both entity and dictionary operations."""
        # Create setting with entity
        setting_entity = Setting(key="entity.setting", value="entity_value")
        setting_entity_id = self.setting_dao.create(setting_entity)
        self.assertIsNotNone(setting_entity_id)
        
        # Create setting with dictionary
        setting_dict = {
            "key": "dict.setting",
            "value": "dict_value"
        }
        setting_dict_id = self.setting_dao.create(setting_dict)
        self.assertIsNotNone(setting_dict_id)
        
        # Retrieve settings in different formats
        # 1. By key -> Entity
        entity_by_key = self.setting_dao.find_by_key("entity.setting")
        self.assertIsInstance(entity_by_key, Setting)
        self.assertEqual(entity_by_key.value, "entity_value")
        
        # 2. By key -> Dict
        dict_by_key = self.setting_dao.find_by_key("dict.setting", as_dict=True)
        self.assertIsInstance(dict_by_key, dict)
        self.assertEqual(dict_by_key["value"], "dict_value")
        
        # Test direct value access
        entity_value = self.setting_dao.get_value("entity.setting")
        self.assertEqual(entity_value, "entity_value")
        
        # Test updating with different patterns
        # 1. Set value creates/updates and returns entity
        updated_entity = self.setting_dao.set_value("entity.setting", "new_entity_value")
        self.assertIsInstance(updated_entity, Setting)
        self.assertEqual(updated_entity.value, "new_entity_value")
        
        # Verify the update worked
        entity_value = self.setting_dao.get_value("entity.setting")
        self.assertEqual(entity_value, "new_entity_value")
        
        # Test settings with different value types
        self.setting_dao.set_value("setting.int", 42)
        self.setting_dao.set_value("setting.float", 3.14)
        self.setting_dao.set_value("setting.bool", True)
        self.setting_dao.set_value("setting.list", [1, 2, 3])
        
        # Verify all value types
        self.assertEqual(self.setting_dao.get_value("setting.int"), 42)
        self.assertEqual(self.setting_dao.get_value("setting.float"), 3.14)
        self.assertEqual(self.setting_dao.get_value("setting.bool"), True)
        self.assertEqual(self.setting_dao.get_value("setting.list"), [1, 2, 3])
        
        # Test prefix filtering
        settings_by_prefix = self.setting_dao.get_settings_by_prefix("setting")
        self.assertEqual(len(settings_by_prefix), 4)
        
    def test_form_dao_entity_dict_interop(self):
        """Test FormDAO with both entity and dictionary operations."""
        # Create user and incident for the form
        user = User(name="Form Test User", call_sign="FORM1")
        user.id = self.user_dao.create(user)
        
        incident = Incident(name="Form Test Incident")
        incident.id = self.incident_dao.create(incident)
        
        # Create form with entity
        form_entity = Form(
            incident_id=incident.id,
            form_type="ICS-213",
            title="Entity Form",
            creator_id=user.id,
            status=FormStatus.DRAFT
        )
        
        # Test creating with content
        form_content = {
            "message": "This is a test form",
            "date": datetime.datetime.now().isoformat()
        }
        
        form_entity_id = self.form_dao.create_with_content(form_entity, form_content, user.id)
        self.assertIsNotNone(form_entity_id)
        
        # Create form with dictionary
        form_dict = {
            "incident_id": incident.id,
            "form_type": "ICS-214",
            "title": "Dict Form",
            "creator_id": user.id,
            "status": str(FormStatus.DRAFT)
        }
        
        form_dict_content = {
            "message": "This is a dictionary form",
            "date": datetime.datetime.now().isoformat()
        }
        
        form_dict_id = self.form_dao.create_with_content(form_dict, form_dict_content, user.id)
        self.assertIsNotNone(form_dict_id)
        
        # Retrieve forms in different formats
        # 1. Entity form with content as entity & dict
        entity_form, entity_content = self.form_dao.find_with_content(form_entity_id)
        self.assertIsInstance(entity_form, Form)
        self.assertEqual(entity_form.title, "Entity Form")
        self.assertEqual(entity_content["message"], "This is a test form")
        
        # 2. Entity form with content as dict
        form_dict, content_dict = self.form_dao.find_with_content(form_entity_id, as_dict=True)
        self.assertIsInstance(form_dict, dict)
        self.assertEqual(form_dict["title"], "Entity Form")
        self.assertEqual(content_dict["message"], "This is a test form")
        
        # Test find by incident
        forms_by_incident = self.form_dao.find_by_incident(incident.id)
        self.assertEqual(len(forms_by_incident), 2)
        
        forms_by_incident_dict = self.form_dao.find_by_incident(incident.id, as_dict=True)
        self.assertEqual(len(forms_by_incident_dict), 2)
        self.assertTrue(all(isinstance(f, dict) for f in forms_by_incident_dict))
        
        # Test find by user
        forms_by_user = self.form_dao.find_by_user(user.id)
        self.assertEqual(len(forms_by_user), 2)
        
        forms_by_user_dict = self.form_dao.find_by_user(user.id, as_dict=True)
        self.assertEqual(len(forms_by_user_dict), 2)
        self.assertTrue(all(isinstance(f, dict) for f in forms_by_user_dict))
        
        # Test find by type
        forms_by_type = self.form_dao.find_by_type("ICS-213")
        self.assertEqual(len(forms_by_type), 1)
        self.assertEqual(forms_by_type[0].id, form_entity_id)
        
    def test_mixed_dao_operations(self):
        """Test operations across multiple DAOs to ensure they work together correctly."""
        # Create a user
        user = User(name="Mixed DAO User", call_sign="MIX1")
        user.id = self.user_dao.create(user)
        
        # Create an incident and track it in settings
        incident = Incident(name="Mixed DAO Incident")
        incident.id = self.incident_dao.create(incident)
        self.setting_dao.set_value("current.incident", incident.id)
        
        # Create a form
        form = Form(
            incident_id=incident.id,
            form_type="ICS-213",
            title="Mixed DAO Form",
            creator_id=user.id,
            status=FormStatus.DRAFT
        )
        form_content = {"message": "Mixed DAO test"}
        form.id = self.form_dao.create_with_content(form, form_content, user.id)
        
        # Track recent forms in settings
        self.setting_dao.set_value("recent.forms", [form.id])
        
        # Verify all entities were created and linked correctly
        current_incident_id = self.setting_dao.get_value("current.incident")
        self.assertEqual(current_incident_id, incident.id)
        
        current_incident = self.incident_dao.find_by_id(current_incident_id)
        self.assertEqual(current_incident.name, "Mixed DAO Incident")
        
        forms_in_incident = self.form_dao.find_by_incident(current_incident.id)
        self.assertEqual(len(forms_in_incident), 1)
        self.assertEqual(forms_in_incident[0].id, form.id)
        
        recent_form_ids = self.setting_dao.get_value("recent.forms")
        self.assertEqual(recent_form_ids, [form.id])
        
        retrieved_form, content = self.form_dao.find_with_content(recent_form_ids[0])
        self.assertEqual(retrieved_form.title, "Mixed DAO Form")
        self.assertEqual(content["message"], "Mixed DAO test")
        
        # Test a complex query - find all forms by a user in active incidents
        active_incidents = self.incident_dao.find_active_incidents(as_dict=True)
        active_incident_ids = [inc['id'] for inc in active_incidents]
        
        forms_by_user = self.form_dao.find_by_user(user.id)
        active_forms = [f for f in forms_by_user if f.incident_id in active_incident_ids]
        
        self.assertEqual(len(active_forms), 1)
        self.assertEqual(active_forms[0].id, form.id)


if __name__ == "__main__":
    unittest.main()
