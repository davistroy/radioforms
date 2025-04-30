#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the specialized DAO implementations with optimized query methods.
"""

import unittest
import tempfile
import datetime
from pathlib import Path
from datetime import timedelta

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.incident_dao_specialized import EnhancedIncidentDAO
from radioforms.database.dao.form_dao_specialized import EnhancedFormDAO
from radioforms.database.dao.user_dao import UserDAO
from radioforms.database.dao.attachment_dao import AttachmentDAO
from radioforms.database.models.user import User
from radioforms.database.models.incident import Incident
from radioforms.database.models.form import Form, FormStatus


class SpecializedDAOsTestCase(unittest.TestCase):
    """Test case for the specialized DAO implementations."""
    
    def setUp(self):
        """Set up a test environment with sample data."""
        # Create a temporary database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_specialized_daos.db"
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create specialized DAO instances
        self.incident_dao = EnhancedIncidentDAO(self.db_manager)
        self.form_dao = EnhancedFormDAO(self.db_manager)
        self.user_dao = UserDAO(self.db_manager)
        self.attachment_dao = AttachmentDAO(self.db_manager, self.temp_dir.name)
        
        # Create test data
        self._create_test_data()
        
    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        self.temp_dir.cleanup()
        
    def _create_test_data(self):
        """Create test data for specialized DAO tests."""
        # Create test users
        self.users = []
        for i in range(3):
            user = User(
                name=f"Test User {i+1}",
                call_sign=f"TEST{i+1}"
            )
            user.id = self.user_dao.create(user)
            self.users.append(user)
            
        # Create test incidents with different dates and statuses
        self.incidents = []
        
        # Incident 1: Active, created 10 days ago
        incident1 = Incident(
            name="Active Recent Incident",
            description="This is an active incident created recently",
            start_date=datetime.datetime.now() - timedelta(days=10)
        )
        incident1.id = self.incident_dao.create(incident1)
        self.incidents.append(incident1)
        
        # Incident 2: Active, created 30 days ago
        incident2 = Incident(
            name="Active Older Incident",
            description="This is an active incident created longer ago",
            start_date=datetime.datetime.now() - timedelta(days=30)
        )
        incident2.id = self.incident_dao.create(incident2)
        self.incidents.append(incident2)
        
        # Incident 3: Closed, created 15 days ago
        incident3 = Incident(
            name="Closed Incident",
            description="This is a closed incident",
            start_date=datetime.datetime.now() - timedelta(days=15),
            end_date=datetime.datetime.now() - timedelta(days=5)
        )
        incident3.id = self.incident_dao.create(incident3)
        self.incidents.append(incident3)
        
        # Incident 4: Active, with "Fire" in the name
        incident4 = Incident(
            name="Wildfire Incident",
            description="This is a fire-related incident",
            start_date=datetime.datetime.now() - timedelta(days=7)
        )
        incident4.id = self.incident_dao.create(incident4)
        self.incidents.append(incident4)
        
        # Create test forms for each incident
        self.forms = []
        
        # Create forms for incident 1 (2 ICS-213, 1 ICS-214)
        for i in range(3):
            form_type = "ICS-213" if i < 2 else "ICS-214"
            # Make the ICS-214 form (i==2) a DRAFT, one ICS-213 a DRAFT, and one FINALIZED
            if i == 0 or i == 2:  # First ICS-213 and the ICS-214 form are DRAFT
                status = FormStatus.DRAFT
            else:
                status = FormStatus.FINALIZED
                
            form = Form(
                incident_id=incident1.id,
                form_type=form_type,
                title=f"Form {i+1} for Incident 1",
                creator_id=self.users[0].id,
                status=status
            )
            
            content = {
                "message": f"Test content for form {i+1}"
            }
            
            form.id = self.form_dao.create_with_content(form, content, self.users[0].id)
            self.forms.append(form)
            
        # Create forms for incident 2 (1 ICS-213)
        form = Form(
            incident_id=incident2.id,
            form_type="ICS-213",
            title=f"Form for Incident 2",
            creator_id=self.users[1].id,
            status=FormStatus.FINALIZED
        )
        
        content = {
            "message": "Test content with urgent request",
            "priority": "high"
        }
        
        form.id = self.form_dao.create_with_content(form, content, self.users[1].id)
        self.forms.append(form)
        
        # Create forms for incident 4 (1 ICS-213, 1 ICS-214)
        for i in range(2):
            form_type = "ICS-213" if i == 0 else "ICS-214" 
            form = Form(
                incident_id=incident4.id,
                form_type=form_type,
                title=f"Form {i+1} for Wildfire",
                creator_id=self.users[2].id,
                status=FormStatus.DRAFT
            )
            
            content = {
                "message": f"Fire-related content for form {i+1}"
            }
            
            form.id = self.form_dao.create_with_content(form, content, self.users[2].id)
            self.forms.append(form)
            
        # Create attachment for the first form
        test_file_path = Path(self.temp_dir.name) / "test_file.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test file for attachment testing.")
            
        self.attachment = self.attachment_dao.create_from_file(
            self.forms[0].id,
            str(test_file_path),
            "test_attachment.txt",
            "text/plain"
        )
    
    def test_find_by_date_range(self):
        """Test finding incidents within a date range."""
        # Date range for the last 20 days
        end_date = datetime.datetime.now()
        start_date = end_date - timedelta(days=20)
        
        # Find incidents in the date range (should find incidents 1, 3, and 4)
        incidents = self.incident_dao.find_by_date_range(start_date, end_date)
        self.assertEqual(len(incidents), 3)
        self.assertIn(self.incidents[0].id, [i.id for i in incidents])
        self.assertIn(self.incidents[2].id, [i.id for i in incidents])
        self.assertIn(self.incidents[3].id, [i.id for i in incidents])
        
        # Only include active incidents (should still be 2)
        active_incidents = self.incident_dao.find_by_date_range(
            start_date, end_date, include_closed=False
        )
        self.assertEqual(len(active_incidents), 2)
        
        # Test with dictionary output
        dict_incidents = self.incident_dao.find_by_date_range(
            start_date, end_date, as_dict=True
        )
        self.assertEqual(len(dict_incidents), 3)
        self.assertTrue(isinstance(dict_incidents[0], dict))
    
    def test_find_recently_active(self):
        """Test finding recently active incidents."""
        # Find incidents active in the last 14 days
        recent_incidents = self.incident_dao.find_recently_active(days=14)
        
        # Should include all 4 incidents since they were all created/updated within 14 days
        self.assertEqual(len(recent_incidents), 4)
        
        # Verify all incidents are in the result
        incident_ids = [i.id for i in recent_incidents]
        for incident in self.incidents:
            self.assertIn(incident.id, incident_ids)
    
    def test_search_incidents(self):
        """Test advanced incident search."""
        # Search for fire-related incidents
        fire_incidents = self.incident_dao.search_incidents(name="Fire")
        self.assertEqual(len(fire_incidents), 1)
        self.assertEqual(fire_incidents[0].id, self.incidents[3].id)
        
        # Search for active incidents
        active_incidents = self.incident_dao.search_incidents(active_only=True)
        self.assertEqual(len(active_incidents), 3)  # Incidents 1, 2, 4
        
        # Search for recent active incidents
        start_date = datetime.datetime.now() - timedelta(days=14)
        recent_active = self.incident_dao.search_incidents(
            active_only=True,
            start_date_from=start_date
        )
        self.assertEqual(len(recent_active), 2)  # Incidents 1 and 4
        
        # Test limit parameter
        limited = self.incident_dao.search_incidents(limit=2)
        self.assertEqual(len(limited), 2)
    
    def test_get_incidents_with_form_counts(self):
        """Test getting incidents with form counts."""
        # Get all incidents with form counts
        incidents_with_counts = self.incident_dao.get_incidents_with_form_counts()
        
        # Should have 4 incidents
        self.assertEqual(len(incidents_with_counts), 4)
        
        # Check form counts
        for inc in incidents_with_counts:
            if inc['id'] == self.incidents[0].id:
                # Incident 1 has 3 forms
                self.assertEqual(inc['form_count'], 3)
            elif inc['id'] == self.incidents[1].id:
                # Incident 2 has 1 form
                self.assertEqual(inc['form_count'], 1)
            elif inc['id'] == self.incidents[2].id:
                # Incident 3 has 0 forms
                self.assertEqual(inc['form_count'], 0)
            elif inc['id'] == self.incidents[3].id:
                # Incident 4 has 2 forms
                self.assertEqual(inc['form_count'], 2)
        
        # Test active_only parameter
        active_with_counts = self.incident_dao.get_incidents_with_form_counts(active_only=True)
        self.assertEqual(len(active_with_counts), 3)  # Excludes incident 3
    
    def test_get_form_stats_by_incident(self):
        """Test getting form statistics for an incident."""
        # Get form stats for incident 1
        stats = self.incident_dao.get_form_stats_by_incident(self.incidents[0].id)
        
        # Incident 1 has 2 draft forms (one ICS-213 and one ICS-214) and 1 finalized form
        self.assertEqual(stats['draft'], 2)
        self.assertEqual(stats['finalized'], 1)
    
    def test_find_incidents_by_form_type(self):
        """Test finding incidents by form type."""
        # Find incidents with ICS-214 forms
        incidents = self.incident_dao.find_incidents_by_form_type("ICS-214")
        
        # Should include incidents 1 and 4
        self.assertEqual(len(incidents), 2)
        self.assertIn(self.incidents[0].id, [i.id for i in incidents])
        self.assertIn(self.incidents[3].id, [i.id for i in incidents])
    
    def test_find_forms_with_content_by_type(self):
        """Test finding forms with content by type."""
        # Find ICS-213 forms with content
        forms_with_content = self.form_dao.find_forms_with_content_by_type("ICS-213")
        
        # Should have 4 ICS-213 forms
        self.assertEqual(len(forms_with_content), 4)
        
        # Check the format of results
        for form, content in forms_with_content:
            self.assertEqual(form.form_type, "ICS-213")
            self.assertIsInstance(content, dict)
            self.assertIn("message", content)
        
        # Test with status filter
        finalized_forms = self.form_dao.find_forms_with_content_by_type(
            "ICS-213", 
            status=FormStatus.FINALIZED
        )
        self.assertEqual(len(finalized_forms), 2)
        
        # Test with dictionary output
        dict_forms = self.form_dao.find_forms_with_content_by_type(
            "ICS-213", 
            as_dict=True
        )
        self.assertEqual(len(dict_forms), 4)
        self.assertTrue(isinstance(dict_forms[0][0], dict))
    
    def test_find_forms_by_status(self):
        """Test finding forms by status."""
        # Find draft forms - should be 4 total (2 from incident 1, 2 from incident 4)
        draft_forms = self.form_dao.find_forms_by_status(FormStatus.DRAFT)
        self.assertEqual(len(draft_forms), 4)
        
        # Find finalized forms for a specific incident - should be 1 for incident 1
        finalized_forms = self.form_dao.find_forms_by_status(
            FormStatus.FINALIZED,
            incident_id=self.incidents[0].id
        )
        self.assertEqual(len(finalized_forms), 1)
        
        # Find draft forms of a specific type (should be 1 from incident 1 and 1 from incident 4)
        draft_ics214 = self.form_dao.find_forms_by_status(
            FormStatus.DRAFT,
            form_type="ICS-214",
            limit=10
        )
        self.assertEqual(len(draft_ics214), 2)
        
        # Check they're from the right incidents
        incident_ids = [form.incident_id for form in draft_ics214]
        self.assertIn(self.incidents[0].id, incident_ids)
        self.assertIn(self.incidents[3].id, incident_ids)
    
    def test_advanced_search(self):
        """Test advanced form search."""
        # Search for forms with "urgent" in the content
        urgent_forms = self.form_dao.advanced_search(content_search="urgent")
        self.assertEqual(len(urgent_forms), 1)
        
        # Search for forms by creator
        user_forms = self.form_dao.advanced_search(creator_id=self.users[0].id)
        self.assertEqual(len(user_forms), 3)
        
        # Search for forms by type and status
        finalized_ics213 = self.form_dao.advanced_search(
            form_type="ICS-213",
            status=FormStatus.FINALIZED
        )
        self.assertEqual(len(finalized_ics213), 2)
        
        # Search with date filters
        recent_date = datetime.datetime.now() - timedelta(days=15)
        recent_forms = self.form_dao.advanced_search(date_from=recent_date)
        self.assertEqual(len(recent_forms), 6)  # All forms were created recently
    
    def test_find_forms_with_attachments(self):
        """Test finding forms with attachments."""
        # Find forms with attachments
        forms_with_attachments = self.form_dao.find_forms_with_attachments()
        self.assertEqual(len(forms_with_attachments), 1)
        self.assertEqual(forms_with_attachments[0].id, self.forms[0].id)
        
        # Test with incident filter
        forms_for_incident = self.form_dao.find_forms_with_attachments(
            incident_id=self.incidents[0].id
        )
        self.assertEqual(len(forms_for_incident), 1)
        
        # Test with dictionary output
        dict_forms = self.form_dao.find_forms_with_attachments(as_dict=True)
        self.assertEqual(len(dict_forms), 1)
        self.assertIsInstance(dict_forms[0], dict)
    
    def test_find_recently_modified_by_user(self):
        """Test finding forms recently modified by a user."""
        # Find forms modified by user 1
        user_forms = self.form_dao.find_recently_modified_by_user(self.users[0].id)
        self.assertEqual(len(user_forms), 3)
        
        # Test with shorter time window - should still return the same forms 
        # as all forms were created just now during test setup
        recent_forms = self.form_dao.find_recently_modified_by_user(self.users[0].id, days=1)
        self.assertEqual(len(recent_forms), 3)
    
    def test_get_form_count_by_type(self):
        """Test getting form counts by type."""
        # Get counts for all forms
        counts = self.form_dao.get_form_count_by_type()
        self.assertEqual(counts["ICS-213"], 4)
        self.assertEqual(counts["ICS-214"], 2)
        
        # Get counts for a specific incident
        inc1_counts = self.form_dao.get_form_count_by_type(incident_id=self.incidents[0].id)
        self.assertEqual(inc1_counts["ICS-213"], 2)
        self.assertEqual(inc1_counts["ICS-214"], 1)


if __name__ == "__main__":
    unittest.main()
