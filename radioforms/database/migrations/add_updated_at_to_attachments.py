#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Migration script to add updated_at column to attachments table.

This script checks if the updated_at column exists in the attachments table,
adds it if it doesn't exist, and updates all existing records to set
updated_at = created_at.
"""

import os
import argparse
import sqlite3
from pathlib import Path


def run_migration(db_path):
    """
    Run the migration to add updated_at column to attachments table.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        True if migration was successful, False otherwise
    """
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col['name'] for col in cursor.fetchall()]
        
        if 'updated_at' in columns:
            print("Column 'updated_at' already exists in 'attachments' table")
            conn.close()
            return True
            
        # Add the column
        print("Adding 'updated_at' column to 'attachments' table...")
        cursor.execute(
            "ALTER TABLE attachments ADD COLUMN updated_at TIMESTAMP"
        )
        
        # Update existing records to set updated_at = created_at
        print("Updating existing records...")
        cursor.execute(
            "UPDATE attachments SET updated_at = created_at"
        )
        
        # Set default value for new records
        print("Setting default value for new records...")
        # SQLite doesn't support adding a column with DEFAULT constraint in ALTER TABLE
        # Instead, we create a temporary table, copy data, drop original, and rename
        cursor.execute('''
        CREATE TABLE attachments_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES forms(id)
        )
        ''')
        
        # Copy data from old table to new table
        cursor.execute('''
        INSERT INTO attachments_new
        SELECT id, form_id, file_path, file_name, file_type, file_size, created_at, updated_at
        FROM attachments
        ''')
        
        # Drop old table and rename new table
        cursor.execute("DROP TABLE attachments")
        cursor.execute("ALTER TABLE attachments_new RENAME TO attachments")
        
        # Create index for form_id if it doesn't exist
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_attachments_form_id ON attachments(form_id)
        ''')
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False


def main():
    """Run the migration script."""
    parser = argparse.ArgumentParser(description='Add updated_at column to attachments table')
    parser.add_argument('--db-path', type=str, required=True, 
                        help='Path to the SQLite database file')
    
    args = parser.parse_args()
    success = run_migration(args.db_path)
    
    if success:
        print("Migration script executed successfully")
    else:
        print("Migration script failed")
        exit(1)
        

if __name__ == "__main__":
    main()
