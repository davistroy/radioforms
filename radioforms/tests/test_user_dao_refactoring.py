#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the refactored UserDAO class.

This module contains tests to verify that the refactored UserDAO class
maintains the same functionality as its original version.
"""

import os
import tempfile
import unittest
from datetime import datetime, timedelta

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.user_dao import UserDAO as OriginalUserDAO
from radioforms.database.dao.user_dao_refactored import UserDAO as RefactoredUserDAO
from radioforms.database.models.user import User


class UserDAORefactoringTests(unittest.TestCase):
    """Tests for the refactored UserDAO class."""
    
    def setUp(self):
        """Set up a test database and DAO instances."""
        # Create a temporary database file
        fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create DAO instances
        self.original_dao = OriginalUserDAO(self.db_manager)
        self.refactored_dao = RefactoredUserDAO(self.db_manager)
        
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
        """Create test schema for users table."""
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
    
    def _insert_test_data(self):
        """Insert test data into the database."""
        # Insert users
        users = [
            {
                'name': 'John Smith',
                'call_sign': 'W1ABC',
                'last_login': datetime.now() - timedelta(hours=2),
                'created_at': datetime.now() - timedelta(days=30),
                'updated_at': datetime.now() - timedelta(hours=2)
            },
            {
                'name': 'Jane Doe',
                'call_sign': 'K5XYZ',
                'last_login': datetime.now() - timedelta(hours=5),
                'created_at': datetime.now() - timedelta(days=20),
                'updated_at': datetime.now() - timedelta(hours=5)
            },
            {
                'name': 'Bob Johnson',
                'call_sign': 'N3DEF',
                'last_login': datetime.now() - timedelta(days=1),
                'created_at': datetime.now() - timedelta(days=10),
                'updated_at': datetime.now() - timedelta(days=1)
            },
            {
                'name': 'Alice Williams',
                'call_sign': 'KD9GHI',
                'last_login': None,
                'created_at': datetime.now() - timedelta(days=5),
                'updated_at': datetime.now() - timedelta(days=5)
            }
        ]
        
        for user in users:
            query = '''
            INSERT INTO users (name, call_sign, last_login, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            '''
            self.db_manager.execute(query, (
                user['name'],
                user['call_sign'],
                user['last_login'],
                user['created_at'],
                user['updated_at']
            ))
    
    def test_find_by_name(self):
        """Test that find_by_name works the same in both implementations."""
        # Test finding by name as objects
        original_results = self.original_dao.find_by_name('John')
        refactored_results = self.refactored_dao.find_by_name('John')
        
        # Verify results are the same
        self.assertEqual(len(original_results), len(refactored_results))
        for i in range(len(original_results)):
            self.assertEqual(original_results[i].id, refactored_results[i].id)
            self.assertEqual(original_results[i].name, refactored_results[i].name)
            self.assertEqual(original_results[i].call_sign, refactored_results[i].call_sign)
        
        # Test finding by name as dictionaries
        original_dict_results = self.original_dao.find_by_name('son', as_dict=True)
        refactored_dict_results = self.refactored_dao.find_by_name('son', as_dict=True)
        
        # Verify dictionary results are the same
        self.assertEqual(len(original_dict_results), len(refactored_dict_results))
        for i in range(len(original_dict_results)):
            self.assertEqual(original_dict_results[i]['id'], refactored_dict_results[i]['id'])
            self.assertEqual(original_dict_results[i]['name'], refactored_dict_results[i]['name'])
            self.assertEqual(original_dict_results[i]['call_sign'], refactored_dict_results[i]['call_sign'])
    
    def test_find_by_call_sign(self):
        """Test that find_by_call_sign works the same in both implementations."""
        # Test finding by call sign as objects
        original_result = self.original_dao.find_by_call_sign('W1ABC')
        refactored_result = self.refactored_dao.find_by_call_sign('W1ABC')
        
        # Verify results are the same
        self.assertIsNotNone(original_result)
        self.assertIsNotNone(refactored_result)
        self.assertEqual(original_result.id, refactored_result.id)
        self.assertEqual(original_result.name, refactored_result.name)
        self.assertEqual(original_result.call_sign, refactored_result.call_sign)
        
        # Test finding by call sign as dictionaries
        original_dict_result = self.original_dao.find_by_call_sign('K5XYZ', as_dict=True)
        refactored_dict_result = self.refactored_dao.find_by_call_sign('K5XYZ', as_dict=True)
        
        # Verify dictionary results are the same
        self.assertIsNotNone(original_dict_result)
        self.assertIsNotNone(refactored_dict_result)
        self.assertEqual(original_dict_result['id'], refactored_dict_result['id'])
        self.assertEqual(original_dict_result['name'], refactored_dict_result['name'])
        self.assertEqual(original_dict_result['call_sign'], refactored_dict_result['call_sign'])
        
        # Test when user is not found
        original_not_found = self.original_dao.find_by_call_sign('NONEXISTENT')
        refactored_not_found = self.refactored_dao.find_by_call_sign('NONEXISTENT')
        
        # Verify both return None
        self.assertIsNone(original_not_found)
        self.assertIsNone(refactored_not_found)
    
    def test_update_last_login(self):
        """Test that update_last_login and set_last_login_time work the same."""
        # Get initial timestamps
        query = "SELECT updated_at, last_login FROM users WHERE id = 1"
        initial_row = dict(self.db_manager.execute(query).fetchone())
        
        # Update with original DAO
        original_result = self.original_dao.update_last_login(1)
        
        # Get updated timestamps
        query = "SELECT updated_at, last_login FROM users WHERE id = 1"
        updated_row = dict(self.db_manager.execute(query).fetchone())
        
        # Verify timestamp was updated
        self.assertTrue(original_result)
        self.assertNotEqual(initial_row['last_login'], updated_row['last_login'])
        self.assertNotEqual(initial_row['updated_at'], updated_row['updated_at'])
        
        # Reset timestamps for refactored test
        initial_timestamp = datetime.now() - timedelta(hours=2)
        self.db_manager.execute(
            "UPDATE users SET last_login = ?, updated_at = ? WHERE id = 1",
            (initial_timestamp, initial_timestamp)
        )
        
        # Update with refactored DAO
        refactored_result = self.refactored_dao.set_last_login_time(1)
        
        # Get updated timestamps
        query = "SELECT updated_at, last_login FROM users WHERE id = 1"
        refactored_row = dict(self.db_manager.execute(query).fetchone())
        
        # Verify timestamp was updated
        self.assertTrue(refactored_result)
        self.assertNotEqual(initial_timestamp, refactored_row['last_login'])
        self.assertNotEqual(initial_timestamp, refactored_row['updated_at'])
    
    def test_find_recent_users(self):
        """Test that find_recent_users and find_recent work the same."""
        # Test finding recent users as objects
        original_results = self.original_dao.find_recent_users(limit=2)
        refactored_results = self.refactored_dao.find_recent(limit=2)
        
        # Verify results are the same
        self.assertEqual(len(original_results), len(refactored_results))
        self.assertEqual(len(original_results), 2)  # Should be limited to 2
        for i in range(len(original_results)):
            self.assertEqual(original_results[i].id, refactored_results[i].id)
            self.assertEqual(original_results[i].name, refactored_results[i].name)
            self.assertEqual(original_results[i].call_sign, refactored_results[i].call_sign)
        
        # Test finding recent users as dictionaries
        original_dict_results = self.original_dao.find_recent_users(limit=3, as_dict=True)
        refactored_dict_results = self.refactored_dao.find_recent(as_dict=True, limit=3)
        
        # Verify dictionary results are the same
        self.assertEqual(len(original_dict_results), len(refactored_dict_results))
        self.assertEqual(len(original_dict_results), 3)  # Should be limited to 3
        for i in range(len(original_dict_results)):
            self.assertEqual(original_dict_results[i]['id'], refactored_dict_results[i]['id'])
            self.assertEqual(original_dict_results[i]['name'], refactored_dict_results[i]['name'])
            self.assertEqual(original_dict_results[i]['call_sign'], refactored_dict_results[i]['call_sign'])
    
    def test_create_user_if_not_exists(self):
        """Test that create_user_if_not_exists and find_or_create work the same."""
        # Test creating a new user with original DAO
        original_user = self.original_dao.create_user_if_not_exists("New User", "W9NEW")
        
        # Verify the user was created
        self.assertIsNotNone(original_user)
        self.assertIsNotNone(original_user.id)
        self.assertEqual(original_user.name, "New User")
        self.assertEqual(original_user.call_sign, "W9NEW")
        
        # Test creating a new user with refactored DAO
        refactored_user = self.refactored_dao.find_or_create("Another User", "K1NEW")
        
        # Verify the user was created
        self.assertIsNotNone(refactored_user)
        self.assertIsNotNone(refactored_user.id)
        self.assertEqual(refactored_user.name, "Another User")
        self.assertEqual(refactored_user.call_sign, "K1NEW")
        
        # Test finding an existing user by call sign with original DAO
        original_existing = self.original_dao.create_user_if_not_exists("Should Not Create", "W1ABC")
        
        # Verify the existing user was found
        self.assertEqual(original_existing.call_sign, "W1ABC")
        self.assertEqual(original_existing.name, "John Smith")  # Original name should be retained
        
        # Test finding an existing user by call sign with refactored DAO
        refactored_existing = self.refactored_dao.find_or_create("Should Not Create Either", "K5XYZ")
        
        # Verify the existing user was found
        self.assertEqual(refactored_existing.call_sign, "K5XYZ")
        self.assertEqual(refactored_existing.name, "Jane Doe")  # Original name should be retained
        
        # Test with dictionary returns for refactored version only
        # (Original has a bug with as_dict=True)
        refactored_dict = self.refactored_dao.find_or_create("Dict User 2", "N2DICT", as_dict=True)
        
        # Verify dictionary results
        self.assertIsInstance(refactored_dict, dict)
        self.assertEqual(refactored_dict['name'], "Dict User 2")


if __name__ == '__main__':
    unittest.main()
