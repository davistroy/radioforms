#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the Database Manager.

This module contains unit tests for the DBManager class to ensure
proper database initialization, query execution, and migration support.
"""

import os
import unittest
import tempfile
import shutil
import sqlite3
from pathlib import Path

from radioforms.database.db_manager import DBManager


class TestDBManager(unittest.TestCase):
    """Unit tests for the Database Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test database path
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # Create db manager
        self.db_manager = DBManager(self.db_path)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Close database connection
        self.db_manager.close()
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_initialization(self):
        """Test database initialization."""
        # Initialize database
        self.db_manager.init_db()
        
        # Verify database file exists
        self.assertTrue(os.path.exists(self.db_path))
        
        # Verify schema version
        version = self.db_manager.get_schema_version()
        self.assertEqual(version, self.db_manager.SCHEMA_VERSION)
        
        # Verify tables were created
        conn = self.db_manager.connect()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        # Check for required tables
        required_tables = [
            "schema_version", "settings", "users", "incidents", 
            "operational_periods", "forms", "form_versions", "attachments"
        ]
        
        for table in required_tables:
            self.assertIn(table, tables)
            
    def test_execute_query(self):
        """Test query execution."""
        # Initialize database
        self.db_manager.init_db()
        
        # Execute a query
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("test_key", "test_value", "2025-01-01"),
            commit=True
        )
        
        # Verify data was inserted
        cursor = self.db_manager.execute(
            "SELECT value FROM settings WHERE key = ?",
            ("test_key",)
        )
        
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['value'], "test_value")
        
    def test_execute_many(self):
        """Test executing multiple queries."""
        # Initialize database
        self.db_manager.init_db()
        
        # Prepare data
        data = [
            ("key1", "value1", "2025-01-01"),
            ("key2", "value2", "2025-01-01"),
            ("key3", "value3", "2025-01-01")
        ]
        
        # Execute query with multiple parameter sets
        self.db_manager.execute_many(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            data,
            commit=True
        )
        
        # Verify data was inserted
        cursor = self.db_manager.execute("SELECT COUNT(*) as count FROM settings")
        row = cursor.fetchone()
        
        self.assertEqual(row['count'], 3)
        
    def test_transaction(self):
        """Test transaction handling."""
        # Initialize database
        self.db_manager.init_db()
        
        # Start transaction
        self.db_manager.begin_transaction()
        
        # Insert data
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("key1", "value1", "2025-01-01")
        )
        
        # Commit transaction
        self.db_manager.commit()
        
        # Verify data was inserted
        cursor = self.db_manager.execute("SELECT COUNT(*) as count FROM settings")
        row = cursor.fetchone()
        self.assertEqual(row['count'], 1)
        
        # Test rollback
        self.db_manager.begin_transaction()
        
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("key2", "value2", "2025-01-01")
        )
        
        # Rollback transaction
        self.db_manager.rollback()
        
        # Verify data was not inserted
        cursor = self.db_manager.execute("SELECT COUNT(*) as count FROM settings")
        row = cursor.fetchone()
        self.assertEqual(row['count'], 1)
        
    def test_query_to_dict(self):
        """Test query_to_dict method."""
        # Initialize database
        self.db_manager.init_db()
        
        # Insert test data
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("key1", "value1", "2025-01-01"),
            commit=True
        )
        
        # Query data as dict
        results = self.db_manager.query_to_dict(
            "SELECT * FROM settings WHERE key = ?",
            ("key1",)
        )
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['key'], "key1")
        self.assertEqual(results[0]['value'], "value1")
        
    def test_migration(self):
        """Test migration support."""
        # Create a minimal database with version 0
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL,
                description TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                attachment_id TEXT PRIMARY KEY,
                form_id TEXT,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                size INTEGER NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        
        # Initialize database which should run migrations
        self.db_manager.init_db()
        
        # Verify schema version
        version = self.db_manager.get_schema_version()
        self.assertEqual(version, self.db_manager.SCHEMA_VERSION)
        
        # Verify migration was applied - attachment table should have updated_at column
        conn = self.db_manager.connect()
        cursor = conn.execute("PRAGMA table_info(attachments)")
        columns = [row['name'] for row in cursor.fetchall()]
        self.assertIn("updated_at", columns)
        
    def test_connection(self):
        """Test database connection."""
        # Get a connection
        conn = self.db_manager.connect()
        self.assertIsNotNone(conn)
        
        # Get another connection - should be the same connection
        conn2 = self.db_manager.connect()
        self.assertEqual(conn, conn2)
        
        # Close connection
        self.db_manager.close()
        
        # Get a new connection
        conn3 = self.db_manager.connect()
        self.assertIsNotNone(conn3)
        self.assertNotEqual(conn, conn3)
        
    def test_backup(self):
        """Test database backup."""
        # Initialize database
        self.db_manager.init_db()
        
        # Add some data
        self.db_manager.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            ("key1", "value1", "2025-01-01"),
            commit=True
        )
        
        # Create backup
        backup_path = self.db_manager.create_backup()
        
        # Verify backup was created
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup contains the data
        backup_conn = sqlite3.connect(backup_path)
        backup_conn.row_factory = sqlite3.Row
        cursor = backup_conn.execute("SELECT value FROM settings WHERE key = ?", ("key1",))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row['value'], "value1")
        
        backup_conn.close()


if __name__ == "__main__":
    unittest.main()
