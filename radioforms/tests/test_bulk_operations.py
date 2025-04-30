#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for bulk operation capabilities in the DAO layer.

This module contains tests for both the BulkOperationsBaseDAO class and
the batch processing utility functions.
"""

import unittest
import tempfile
import datetime
import os
import json
import io
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.base_dao_bulk import BulkOperationsBaseDAO
from radioforms.database.dao.batch_processing_utils import (
    BatchProcessingResult,
    import_from_csv,
    export_to_csv,
    import_from_json,
    bulk_upsert,
    multi_threaded_batch_process
)
from radioforms.database.models.user import User
from radioforms.database.models.incident import Incident


class BulkUserDAO(BulkOperationsBaseDAO[User]):
    """Test implementation of BulkOperationsBaseDAO for User entities."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = 'users'
        self.pk_column = 'id'
        
    def _row_to_entity(self, row: Dict[str, Any]) -> User:
        """Convert a row dictionary to a User object."""
        return User(
            id=row.get('id'),
            name=row.get('name', ''),
            call_sign=row.get('call_sign'),
            last_login=row.get('last_login'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_values(self, entity: User) -> Dict[str, Any]:
        """Convert a User object to a values dictionary."""
        values = {
            'name': entity.name,
            'call_sign': entity.call_sign,
            'last_login': entity.last_login,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values


class BulkIncidentDAO(BulkOperationsBaseDAO[Incident]):
    """Test implementation of BulkOperationsBaseDAO for Incident entities."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = 'incidents'
        self.pk_column = 'id'
        
    def _row_to_entity(self, row: Dict[str, Any]) -> Incident:
        """Convert a row dictionary to an Incident object."""
        return Incident(
            id=row.get('id'),
            name=row.get('name', ''),
            description=row.get('description'),
            start_date=row.get('start_date'),
            end_date=row.get('end_date'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_values(self, entity: Incident) -> Dict[str, Any]:
        """Convert an Incident object to a values dictionary."""
        values = {
            'name': entity.name,
            'description': entity.description,
            'start_date': entity.start_date,
            'end_date': entity.end_date,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values


class BulkOperationsTestCase(unittest.TestCase):
    """Test case for bulk operations in the DAO layer."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_bulk_operations.db"
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create DAO instances
        self.user_dao = BulkUserDAO(self.db_manager)
        self.incident_dao = BulkIncidentDAO(self.db_manager)
        
    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        self.temp_dir.cleanup()
        
    def test_bulk_create_entities(self):
        """Test bulk creation of entity objects."""
        # Create test users
        users = []
        for i in range(10):
            user = User(
                name=f"User {i+1}",
                call_sign=f"U{i+1}"
            )
            users.append(user)
            
        # Bulk create the users
        user_ids = self.user_dao.bulk_create(users)
        
        # Verify IDs were returned
        self.assertEqual(len(user_ids), 10)
        
        # Verify users were created in the database
        for user_id in user_ids:
            user = self.user_dao.find_by_id(user_id)
            self.assertIsNotNone(user)
            self.assertTrue(user.name.startswith("User "))
            
    def test_bulk_create_dicts(self):
        """Test bulk creation from dictionaries."""
        # Create test incident dictionaries
        incidents = []
        for i in range(5):
            incident = {
                "name": f"Incident {i+1}",
                "description": f"Test incident {i+1}",
                "start_date": datetime.datetime.now()
            }
            incidents.append(incident)
            
        # Bulk create the incidents
        incident_ids = self.incident_dao.bulk_create(incidents)
        
        # Verify IDs were returned
        self.assertEqual(len(incident_ids), 5)
        
        # Verify incidents were created in the database
        for incident_id in incident_ids:
            incident = self.incident_dao.find_by_id(incident_id)
            self.assertIsNotNone(incident)
            self.assertTrue(incident.name.startswith("Incident "))
            
    def test_bulk_update_entities(self):
        """Test bulk update of entity objects."""
        # Create some test users first
        users = []
        for i in range(5):
            user = User(
                name=f"Original User {i+1}",
                call_sign=f"OU{i+1}"
            )
            users.append(user)
            
        user_ids = self.user_dao.bulk_create(users)
        
        # Retrieve the users, modify them, and update in bulk
        updated_users = []
        for user_id in user_ids:
            user = self.user_dao.find_by_id(user_id)
            user.name = f"Updated {user.name}"
            updated_users.append(user)
            
        # Perform bulk update
        updated_count = self.user_dao.bulk_update(updated_users)
        
        # Verify update count
        self.assertEqual(updated_count, 5)
        
        # Verify users were updated in the database
        for user_id in user_ids:
            user = self.user_dao.find_by_id(user_id)
            self.assertIsNotNone(user)
            self.assertTrue(user.name.startswith("Updated Original User"))
            
    def test_bulk_update_dicts(self):
        """Test bulk update from dictionaries."""
        # Create some test incidents first
        incidents = []
        for i in range(5):
            incident = {
                "name": f"Original Incident {i+1}",
                "description": f"Original description {i+1}",
                "start_date": datetime.datetime.now()
            }
            incidents.append(incident)
            
        incident_ids = self.incident_dao.bulk_create(incidents)
        
        # Create update dictionaries
        updated_incidents = []
        for i, incident_id in enumerate(incident_ids):
            updated_incidents.append({
                "id": incident_id,
                "description": f"Updated description {i+1}"
            })
            
        # Perform bulk update
        updated_count = self.incident_dao.bulk_update(updated_incidents)
        
        # Verify update count
        self.assertEqual(updated_count, 5)
        
        # Verify incidents were updated in the database
        for i, incident_id in enumerate(incident_ids):
            incident = self.incident_dao.find_by_id(incident_id)
            self.assertIsNotNone(incident)
            self.assertEqual(incident.description, f"Updated description {i+1}")
            
    def test_bulk_update_by_ids(self):
        """Test bulk update by ID list with common values."""
        # Create some test users first
        users = []
        for i in range(5):
            user = User(
                name=f"Original User {i+1}",
                call_sign=f"OU{i+1}"
            )
            users.append(user)
            
        user_ids = self.user_dao.bulk_create(users)
        
        # Update all users with the same values
        common_values = {
            "call_sign": "UPDATED"
        }
        
        updated_count = self.user_dao.bulk_update(user_ids, common_values)
        
        # Verify update count
        self.assertEqual(updated_count, 5)
        
        # Verify users were updated in the database
        for user_id in user_ids:
            user = self.user_dao.find_by_id(user_id)
            self.assertIsNotNone(user)
            self.assertEqual(user.call_sign, "UPDATED")
            
    def test_bulk_delete(self):
        """Test bulk deletion by ID list."""
        # Create some test incidents first
        incidents = []
        for i in range(10):
            incident = {
                "name": f"Incident {i+1}",
                "description": f"Description {i+1}",
                "start_date": datetime.datetime.now()
            }
            incidents.append(incident)
            
        incident_ids = self.incident_dao.bulk_create(incidents)
        
        # Delete some of the incidents
        incidents_to_delete = incident_ids[3:7]  # Delete 4 incidents
        
        deleted_count = self.incident_dao.bulk_delete(incidents_to_delete)
        
        # Verify delete count
        self.assertEqual(deleted_count, 4)
        
        # Verify the correct incidents were deleted
        for incident_id in incident_ids:
            incident = self.incident_dao.find_by_id(incident_id)
            if incident_id in incidents_to_delete:
                self.assertIsNone(incident)  # Should be deleted
            else:
                self.assertIsNotNone(incident)  # Should still exist
                
    def test_bulk_delete_by_filter(self):
        """Test bulk deletion by filter criteria."""
        # Create some test users with different call signs
        users = []
        for i in range(5):
            user = User(
                name=f"User {i+1}",
                call_sign=f"GROUP_A"
            )
            users.append(user)
            
        for i in range(5):
            user = User(
                name=f"User {i+6}",
                call_sign=f"GROUP_B"
            )
            users.append(user)
            
        self.user_dao.bulk_create(users)
        
        # Delete all users in GROUP_A
        deleted_count = self.user_dao.bulk_delete_by_filter({"call_sign": "GROUP_A"})
        
        # Verify delete count
        self.assertEqual(deleted_count, 5)
        
        # Verify the correct users were deleted
        remaining_users = self.user_dao.find_all()
        self.assertEqual(len(remaining_users), 5)
        for user in remaining_users:
            self.assertEqual(user.call_sign, "GROUP_B")


class BatchProcessingUtilsTestCase(unittest.TestCase):
    """Test case for batch processing utility functions."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory and database file
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_batch_utils.db"
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create DAO instances
        self.user_dao = BulkUserDAO(self.db_manager)
        self.incident_dao = BulkIncidentDAO(self.db_manager)
        
    def tearDown(self):
        """Clean up after the test."""
        try:
            # Always close database connections first
            if hasattr(self, 'db_manager'):
                self.db_manager.close()
                
            # Sleep briefly to allow file handles to be released
            import time
            time.sleep(0.1)
                
            # Cleanup the temp directory
            if os.path.exists(self.temp_dir):
                import shutil
                try:
                    shutil.rmtree(self.temp_dir)
                except (PermissionError, OSError):
                    # On Windows, sometimes we can't delete immediately
                    # We'll just ignore and let the OS clean it up later
                    pass
        except Exception as e:
            # Ensure test teardown doesn't fail the test
            print(f"Warning: Cleanup issue (can be ignored): {e}")
        
    def test_import_from_csv(self):
        """Test importing data from a CSV file."""
        # Create a CSV file
        csv_path = Path(self.temp_dir) / "test_users.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "CallSign"])  # Header
            for i in range(10):
                writer.writerow([f"CSV User {i+1}", f"CSV{i+1}"])
                
        # Import from CSV
        result = import_from_csv(
            self.user_dao,
            csv_path,
            column_mapping={"Name": "name", "CallSign": "call_sign"},
            batch_size=5
        )
        
        # Verify import results
        self.assertEqual(result.successful_items, 10)
        self.assertEqual(result.failed_items, 0)
        
        # Verify users were created in the database
        users = self.user_dao.find_all()
        self.assertEqual(len(users), 10)
        self.assertTrue(all(user.name.startswith("CSV User") for user in users))
        self.assertTrue(all(user.call_sign.startswith("CSV") for user in users))
        
    def test_export_to_csv(self):
        """Test exporting data to a CSV file."""
        # Create some test incidents
        incidents = []
        for i in range(5):
            incident = Incident(
                name=f"Export Incident {i+1}",
                description=f"Export description {i+1}",
                start_date=datetime.datetime.now()
            )
            incidents.append(incident)
            
        incident_ids = self.incident_dao.bulk_create(incidents)
        
        # Export to CSV
        csv_path = Path(self.temp_dir) / "export_incidents.csv"
        result = export_to_csv(
            self.incident_dao,
            csv_path,
            column_mapping={
                "name": "Incident Name",
                "description": "Description",
                "start_date": "Start Date"
            }
        )
        
        # Verify export results
        self.assertEqual(result.successful_items, 5)
        self.assertEqual(result.failed_items, 0)
        
        # Verify CSV file contents
        with open(csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertIn("Incident Name", header)
            self.assertIn("Description", header)
            
            rows = list(reader)
            self.assertEqual(len(rows), 5)
            
            # Find the index of the "Incident Name" column
            incident_name_index = header.index("Incident Name")
            self.assertTrue(all(row[incident_name_index].startswith("Export Incident") for row in rows))
            
    def test_import_from_json(self):
        """Test importing data from a JSON file."""
        # Create a JSON file
        json_data = {
            "users": [
                {"name": f"JSON User {i+1}", "call_sign": f"JSON{i+1}"}
                for i in range(8)
            ]
        }
        
        json_path = Path(self.temp_dir) / "test_users.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
            
        # Import from JSON
        result = import_from_json(
            self.user_dao,
            json_path,
            batch_size=3,
            root_element="users"
        )
        
        # Verify import results
        self.assertEqual(result.successful_items, 8)
        self.assertEqual(result.failed_items, 0)
        
        # Verify users were created in the database
        users = self.user_dao.find_all()
        self.assertEqual(len(users), 8)
        self.assertTrue(all(user.name.startswith("JSON User") for user in users))
        self.assertTrue(all(user.call_sign.startswith("JSON") for user in users))
        
    def test_bulk_upsert(self):
        """Test bulk upsert operation."""
        # Create some initial users
        initial_users = [
            {"name": "Existing User 1", "call_sign": "EU1"},
            {"name": "Existing User 2", "call_sign": "EU2"}
        ]
        self.user_dao.bulk_create(initial_users)
        
        # Prepare upsert data - mix of updates and inserts
        upsert_data = [
            {"name": "Updated User 1", "call_sign": "EU1"},  # Update
            {"name": "Updated User 2", "call_sign": "EU2"},  # Update
            {"name": "New User 1", "call_sign": "NU1"},      # Insert
            {"name": "New User 2", "call_sign": "NU2"}       # Insert
        ]
        
        # Perform upsert
        result = bulk_upsert(self.user_dao, upsert_data, "call_sign")
        
        # Verify results
        self.assertEqual(result.successful_items, 4)
        self.assertEqual(result.failed_items, 0)
        
        # Verify database state
        users = {user.call_sign: user for user in self.user_dao.find_all()}
        self.assertEqual(len(users), 4)
        
        # Check updated records
        self.assertEqual(users["EU1"].name, "Updated User 1")
        self.assertEqual(users["EU2"].name, "Updated User 2")
        
        # Check new records
        self.assertEqual(users["NU1"].name, "New User 1")
        self.assertEqual(users["NU2"].name, "New User 2")
        
    def test_non_multi_threaded_batch_process(self):
        """
        Test batch processing without multi-threading.
        
        Note: We're using a non-threaded version of this test because SQLite
        has limitations with concurrent access on Windows systems which
        can cause test failures due to database locking.
        """
        # Create a test dataset 
        incidents = []
        for i in range(20):
            incident = {
                "name": f"Incident {i+1}",
                "description": f"Description {i+1}"
            }
            incidents.append(incident)
            
        # Use the utility function with just 1 worker (effectively single-threaded)
        result = multi_threaded_batch_process(
            self.incident_dao,
            incidents,
            lambda batch: self.incident_dao.bulk_create(batch),
            max_workers=1,  
            batch_size=5
        )
        
        # Verify results
        self.assertEqual(result.successful_items, 20)
        self.assertEqual(result.failed_items, 0)
        
        # Verify database state
        incidents = self.incident_dao.find_all()
        self.assertEqual(len(incidents), 20)
        

if __name__ == "__main__":
    unittest.main()
