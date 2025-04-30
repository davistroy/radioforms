#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the refactored DAO classes.

This module contains tests to verify that the refactored DAO classes
maintain the same functionality as their original versions.
"""

import os
import tempfile
import unittest
from datetime import datetime, timedelta

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.incident_dao import IncidentDAO as OriginalIncidentDAO
from radioforms.database.dao.incident_dao_refactored import IncidentDAO as RefactoredIncidentDAO
from radioforms.database.models.incident import Incident


class IncidentDAORefactoringTests(unittest.TestCase):
    """Tests for the refactored IncidentDAO class."""
    
    def setUp(self):
        """Set up a test database and DAO instances."""
        # Create a temporary database file
        fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create DAO instances
        self.original_dao = OriginalIncidentDAO(self.db_manager)
        self.refactored_dao = RefactoredIncidentDAO(self.db_manager)
        
        # Create test schema
        self._create_test_schema()
        
        # Add test data
        self._insert_test_data()
    
    def tearDown(self):
        """Clean up resources."""
        self.db_manager.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def _create_test_schema(self):
        """Create test schema for incidents table."""
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
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
        )
        ''')
    
    def _insert_test_data(self):
        """Insert test data into the database."""
        # Insert incidents
        incidents = [
            {
                'name': 'Test Incident 1',
                'description': 'Active incident for testing',
                'start_date': datetime.now() - timedelta(days=2),
                'end_date': None,
                'created_at': datetime.now() - timedelta(days=2),
                'updated_at': datetime.now() - timedelta(days=1)
            },
            {
                'name': 'Test Incident 2',
                'description': 'Closed incident for testing',
                'start_date': datetime.now() - timedelta(days=5),
                'end_date': datetime.now() - timedelta(days=3),
                'created_at': datetime.now() - timedelta(days=5),
                'updated_at': datetime.now() - timedelta(days=3)
            },
            {
                'name': 'Fire Drill Exercise',
                'description': 'Training exercise',
                'start_date': datetime.now() - timedelta(days=1),
                'end_date': None,
                'created_at': datetime.now() - timedelta(days=1),
                'updated_at': datetime.now() - timedelta(hours=12)
            }
        ]
        
        for incident in incidents:
            query = '''
            INSERT INTO incidents (name, description, start_date, end_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            self.db_manager.execute(query, (
                incident['name'],
                incident['description'],
                incident['start_date'],
                incident['end_date'],
                incident['created_at'],
                incident['updated_at']
            ))
        
        # Insert some test forms
        forms = [
            {
                'incident_id': 1,
                'form_type': 'ICS-213',
                'title': 'General Message Form',
                'status': 'draft',
                'creator_id': None,
                'created_at': datetime.now() - timedelta(days=1),
                'updated_at': datetime.now() - timedelta(days=1)
            },
            {
                'incident_id': 1,
                'form_type': 'ICS-214',
                'title': 'Activity Log',
                'status': 'draft',
                'creator_id': None,
                'created_at': datetime.now() - timedelta(hours=12),
                'updated_at': datetime.now() - timedelta(hours=12)
            },
            {
                'incident_id': 3,
                'form_type': 'ICS-213',
                'title': 'Training Message',
                'status': 'draft',
                'creator_id': None,
                'created_at': datetime.now() - timedelta(hours=6),
                'updated_at': datetime.now() - timedelta(hours=6)
            }
        ]
        
        for form in forms:
            query = '''
            INSERT INTO forms (incident_id, form_type, title, status, creator_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            self.db_manager.execute(query, (
                form['incident_id'],
                form['form_type'],
                form['title'],
                form['status'],
                form['creator_id'],
                form['created_at'],
                form['updated_at']
            ))
    
    def test_create(self):
        """Test that create method works the same in both implementations."""
        # Test creating an incident from a model object
        incident = Incident(
            name="New Incident",
            description="Test incident from model",
            start_date=datetime.now()
        )
        
        original_id = self.original_dao.create(incident)
        
        # Reset the incident to ensure it doesn't have an ID
        incident = Incident(
            name="New Incident",
            description="Test incident from model",
            start_date=datetime.now()
        )
        
        refactored_id = self.refactored_dao.create(incident)
        
        # Verify both methods return valid IDs
        self.assertIsInstance(original_id, int)
        self.assertIsInstance(refactored_id, int)
        self.assertGreater(original_id, 0)
        self.assertGreater(refactored_id, 0)
        
        # Test creating an incident from a dictionary
        incident_dict = {
            'name': 'Dictionary Incident',
            'description': 'Test incident from dictionary',
            'start_date': datetime.now()
        }
        
        original_id = self.original_dao.create(incident_dict)
        refactored_id = self.refactored_dao.create(incident_dict)
        
        # Verify both methods return valid IDs
        self.assertIsInstance(original_id, int)
        self.assertIsInstance(refactored_id, int)
        self.assertGreater(original_id, 0)
        self.assertGreater(refactored_id, 0)
    
    def test_find_by_name(self):
        """Test that find_by_name works the same in both implementations."""
        # Test finding by name as objects
        original_results = self.original_dao.find_by_name('Fire')
        refactored_results = self.refactored_dao.find_by_name('Fire')
        
        # Verify results are the same
        self.assertEqual(len(original_results), len(refactored_results))
        for i in range(len(original_results)):
            self.assertEqual(original_results[i].id, refactored_results[i].id)
            self.assertEqual(original_results[i].name, refactored_results[i].name)
        
        # Test finding by name as dictionaries
        original_dict_results = self.original_dao.find_by_name('Test', as_dict=True)
        refactored_dict_results = self.refactored_dao.find_by_name('Test', as_dict=True)
        
        # Verify dictionary results are the same
        self.assertEqual(len(original_dict_results), len(refactored_dict_results))
        for i in range(len(original_dict_results)):
            self.assertEqual(original_dict_results[i]['id'], refactored_dict_results[i]['id'])
            self.assertEqual(original_dict_results[i]['name'], refactored_dict_results[i]['name'])
    
    def test_find_all(self):
        """Test that find_all (refactored) and find_all_incidents (original) work the same."""
        # Test finding all incidents as objects
        original_results = self.original_dao.find_all_incidents()
        refactored_results = self.refactored_dao.find_all()
        
        # Verify results are the same
        self.assertEqual(len(original_results), len(refactored_results))
        for i in range(len(original_results)):
            self.assertEqual(original_results[i].id, refactored_results[i].id)
            self.assertEqual(original_results[i].name, refactored_results[i].name)
        
        # Test finding all incidents as dictionaries
        original_dict_results = self.original_dao.find_all_incidents(as_dict=True)
        refactored_dict_results = self.refactored_dao.find_all(as_dict=True)
        
        # Verify dictionary results are the same
        self.assertEqual(len(original_dict_results), len(refactored_dict_results))
        for i in range(len(original_dict_results)):
            self.assertEqual(original_dict_results[i]['id'], refactored_dict_results[i]['id'])
            self.assertEqual(original_dict_results[i]['name'], refactored_dict_results[i]['name'])
        
        # Test finding all incidents with custom ordering
        original_ordered = self.original_dao.find_all_incidents(order_by="name ASC")
        refactored_ordered = self.refactored_dao.find_all(order_by="name ASC")
        
        # Verify ordered results are the same
        self.assertEqual(len(original_ordered), len(refactored_ordered))
        for i in range(len(original_ordered)):
            self.assertEqual(original_ordered[i].id, refactored_ordered[i].id)
            self.assertEqual(original_ordered[i].name, refactored_ordered[i].name)
    
    def test_find_active(self):
        """Test that find_active (refactored) and find_active_incidents (original) work the same."""
        # Test finding active incidents as objects
        original_results = self.original_dao.find_active_incidents()
        refactored_results = self.refactored_dao.find_active()
        
        # Verify results are the same
        self.assertEqual(len(original_results), len(refactored_results))
        for i in range(len(original_results)):
            self.assertEqual(original_results[i].id, refactored_results[i].id)
            self.assertEqual(original_results[i].name, refactored_results[i].name)
        
        # Test finding active incidents as dictionaries
        original_dict_results = self.original_dao.find_active_incidents(as_dict=True)
        refactored_dict_results = self.refactored_dao.find_active(as_dict=True)
        
        # Verify dictionary results are the same
        self.assertEqual(len(original_dict_results), len(refactored_dict_results))
        for i in range(len(original_dict_results)):
            self.assertEqual(original_dict_results[i]['id'], refactored_dict_results[i]['id'])
            self.assertEqual(original_dict_results[i]['name'], refactored_dict_results[i]['name'])
    
    def test_close_and_reopen_incident(self):
        """Test that closing and reopening incidents works the same in both implementations."""
        # Test closing an incident (original: close_incident, refactored: set_incident_closed)
        original_close_result = self.original_dao.close_incident(1)
        
        # Reset for refactored test
        self.db_manager.execute("UPDATE incidents SET end_date = NULL WHERE id = 1")
        
        refactored_close_result = self.refactored_dao.set_incident_closed(1)
        
        # Verify results are the same
        self.assertEqual(original_close_result, refactored_close_result)
        
        # Test reopening an incident (original: reopen_incident, refactored: set_incident_active)
        original_reopen_result = self.original_dao.reopen_incident(2)
        
        # Reset for refactored test
        self.db_manager.execute("UPDATE incidents SET end_date = ? WHERE id = 2", 
                              (datetime.now() - timedelta(days=3),))
        
        refactored_reopen_result = self.refactored_dao.set_incident_active(2)
        
        # Verify results are the same
        self.assertEqual(original_reopen_result, refactored_reopen_result)
    
    def test_find_forms_by_incident(self):
        """Test that find_forms_by_incident (refactored) and find_forms_for_incident (original) work the same."""
        # Test finding forms for an incident
        original_results = self.original_dao.find_forms_for_incident(1)
        refactored_results = self.refactored_dao.find_forms_by_incident(1)
        
        # Verify results are the same
        self.assertEqual(len(original_results), len(refactored_results))
        for i in range(len(original_results)):
            self.assertEqual(original_results[i]['id'], refactored_results[i]['id'])
            self.assertEqual(original_results[i]['form_type'], refactored_results[i]['form_type'])
            self.assertEqual(original_results[i]['title'], refactored_results[i]['title'])
    
    def test_incident_stats(self):
        """Test that incident stats work the same in both implementations."""
        # Test getting incident statistics
        original_stats = self.original_dao.get_incident_stats()
        refactored_stats = self.refactored_dao.find_incident_stats()
        
        # Verify stats are the same
        self.assertEqual(original_stats['total'], refactored_stats['total'])
        self.assertEqual(original_stats['active'], refactored_stats['active'])
        self.assertEqual(original_stats['closed'], refactored_stats['closed'])


if __name__ == '__main__':
    unittest.main()
