#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the database implementation to verify the schema design and operations.
"""

import os
import unittest
import tempfile
import sqlite3
from pathlib import Path

from radioforms.database.db_manager import DatabaseManager


class DatabaseSchemaTestCase(unittest.TestCase):
    """Test case for database schema implementation."""
    
    def setUp(self):
        """Set up a test database."""
        # Create a temporary file for the test database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_radioforms.db"
        
        # Create a database manager instance
        self.db_manager = DatabaseManager(self.db_path)
        
    def tearDown(self):
        """Clean up resources."""
        # Close the database connection
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_database_creation(self):
        """Test that the database file is created."""
        self.assertTrue(self.db_path.exists(), "Database file should be created")
        
    def test_tables_created(self):
        """Test that all required tables are created."""
        # Get a connection to the database
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()
        
        # Query for all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check that all expected tables exist
        expected_tables = [
            'users', 'incidents', 'forms', 'form_versions', 
            'attachments', 'settings'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} should exist")
            
    def test_wal_mode(self):
        """Test that WAL mode is enabled."""
        # Get a connection to the database
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()
        
        # Check journal mode
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0].upper()
        
        self.assertEqual(journal_mode, "WAL", "Journal mode should be WAL")
        
    def test_foreign_keys_enabled(self):
        """Test that foreign keys are enabled."""
        # Get a connection to the database
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()
        
        # Check foreign keys setting
        cursor.execute("PRAGMA foreign_keys;")
        foreign_keys = cursor.fetchone()[0]
        
        self.assertEqual(foreign_keys, 1, "Foreign keys should be enabled")
        
    def test_transaction_functionality(self):
        """Test transaction functionality."""
        # Test successful transaction
        try:
            with self.db_manager.transaction() as tx:
                tx.execute("INSERT INTO users (name, call_sign) VALUES (?, ?)", 
                          ("Test User", "TEST1"))
                
            # Verify the user was inserted
            cursor = self.db_manager.execute("SELECT * FROM users WHERE name = ?", ("Test User",))
            user = cursor.fetchone()
            self.assertIsNotNone(user, "User should be inserted in successful transaction")
            
            # Test rollback
            try:
                with self.db_manager.transaction() as tx:
                    tx.execute("INSERT INTO users (name, call_sign) VALUES (?, ?)", 
                              ("Rollback User", "TEST2"))
                    # Raise an exception to trigger rollback
                    raise Exception("Test rollback")
            except Exception:
                pass
                
            # Verify the user was not inserted
            cursor = self.db_manager.execute("SELECT * FROM users WHERE name = ?", ("Rollback User",))
            user = cursor.fetchone()
            self.assertIsNone(user, "User should not be inserted when transaction is rolled back")
        except Exception as e:
            self.fail(f"Transaction test failed with exception: {e}")
            
    def test_table_fields(self):
        """Test that tables have the expected fields."""
        # Get a connection to the database
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()
        
        # Define expected fields for each table
        expected_fields = {
            'users': ['id', 'name', 'call_sign', 'last_login', 'created_at', 'updated_at'],
            'incidents': ['id', 'name', 'description', 'start_date', 'end_date', 'created_at', 'updated_at'],
            'forms': ['id', 'incident_id', 'form_type', 'title', 'creator_id', 'status', 'created_at', 'updated_at'],
            'form_versions': ['id', 'form_id', 'version_number', 'content', 'created_by', 'created_at'],
            'attachments': ['id', 'form_id', 'file_path', 'file_name', 'file_type', 'file_size', 'created_at'],
            'settings': ['id', 'key', 'value', 'created_at', 'updated_at']
        }
        
        # Check fields for each table
        for table, fields in expected_fields.items():
            cursor.execute(f"PRAGMA table_info({table});")
            table_fields = [row[1] for row in cursor.fetchall()]
            
            for field in fields:
                self.assertIn(field, table_fields, f"Field {field} should exist in table {table}")


if __name__ == "__main__":
    unittest.main()
