#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test for attachment schema migration adding updated_at column.
"""

import os
import unittest
import tempfile
import sqlite3
from datetime import datetime
from pathlib import Path

from radioforms.database.models.attachment import Attachment
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.attachment_dao import AttachmentDAO
from radioforms.database.migrations.add_updated_at_to_attachments import run_migration


class TestAttachmentSchemaMigration(unittest.TestCase):
    """Test the attachment schema migration."""
    
    def setUp(self):
        """Set up test environment with a temporary database."""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Initialize the database with test schema (without updated_at column)
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
        CREATE TABLE forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_type TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create attachments table without updated_at column
        conn.execute('''
        CREATE TABLE attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES forms(id)
        )
        ''')
        
        # Create a test form
        conn.execute('''
        INSERT INTO forms (form_type, name, created_at)
        VALUES (?, ?, ?)
        ''', ('ICS-213', 'Test Form', datetime.now().isoformat()))
        
        form_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        # Insert test attachments
        conn.execute('''
        INSERT INTO attachments (form_id, file_path, file_name, file_type, file_size, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (form_id, '/path/to/test.txt', 'test.txt', 'text/plain', 1024, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Create DatabaseManager for testing
        self.db_manager = DatabaseManager(self.db_path)
        self.attachment_dao = AttachmentDAO(self.db_manager)
        
    def tearDown(self):
        """Clean up resources after tests."""
        self.db_manager.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
    def test_add_updated_at_column(self):
        """Test the migration adds the updated_at column correctly."""
        # Verify column doesn't exist before migration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col[1] for col in cursor.fetchall()]
        self.assertNotIn('updated_at', columns)
        conn.close()
        
        # Run the migration
        success = run_migration(self.db_path)
        self.assertTrue(success)
        
        # Verify column exists after migration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col[1] for col in cursor.fetchall()]
        self.assertIn('updated_at', columns)
        
        # Verify existing records have updated_at = created_at
        cursor.execute("SELECT created_at, updated_at FROM attachments")
        rows = cursor.fetchall()
        self.assertTrue(len(rows) > 0)
        for row in rows:
            created_at, updated_at = row
            self.assertEqual(created_at, updated_at)
        
        conn.close()
        
    def test_dao_functionality_after_migration(self):
        """Test the AttachmentDAO works correctly after migration."""
        # Run the migration
        run_migration(self.db_path)
        
        # Perform operations with the DAO
        # 1. Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'Test content')
            temp_path = temp_file.name
        
        try:
            # 2. Create attachment
            form_id = 1  # From setUp
            attachment = self.attachment_dao.create_from_file(
                form_id=form_id,
                file_path=temp_path,
                file_name='new_test.txt',
                file_type='text/plain'
            )
            
            # 3. Verify attachment properties
            self.assertIsNotNone(attachment.id)
            self.assertEqual(attachment.form_id, form_id)
            self.assertEqual(attachment.file_name, 'new_test.txt')
            self.assertEqual(attachment.file_type, 'text/plain')
            self.assertIsNotNone(attachment.updated_at)
            
            # 4. Retrieve attachment 
            retrieved = self.attachment_dao.find_by_id(attachment.id)
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.id, attachment.id)
            self.assertEqual(retrieved.updated_at, attachment.updated_at)
            
            # 5. Update attachment and check updated_at changes
            original_updated_at = retrieved.updated_at
            
            # Force a timestamp difference
            import time
            time.sleep(0.01)
            
            retrieved.file_name = 'updated_name.txt'
            # Manually call touch() to update the timestamp
            retrieved.touch()
            self.attachment_dao.update(retrieved)
            
            updated = self.attachment_dao.find_by_id(attachment.id)
            self.assertEqual(updated.file_name, 'updated_name.txt')
            self.assertNotEqual(updated.updated_at, original_updated_at)
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
