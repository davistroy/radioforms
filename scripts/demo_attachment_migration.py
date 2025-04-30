#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo script for the attachment schema migration.
Creates a test database and applies the migration to demonstrate functionality.
"""

import os
import sys
import argparse
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from radioforms.database.migrations.add_updated_at_to_attachments import run_migration


def create_test_db(db_path):
    """
    Create a test database with schema and sample data.
    
    Args:
        db_path: Path where to create the database
        
    Returns:
        True if database was created successfully, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to the database (will create it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Creating test database at: {db_path}")
        
        # Create forms table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_type TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create attachments table without updated_at column
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
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
        
        # Insert sample data
        cursor.execute('''
        INSERT INTO forms (form_type, name, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ''', ('ICS-213', 'General Message Form', datetime.now().isoformat(), datetime.now().isoformat()))
        
        cursor.execute('''
        INSERT INTO forms (form_type, name, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ''', ('ICS-214', 'Activity Log', datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Get the form IDs
        form_ids = [row[0] for row in cursor.execute("SELECT id FROM forms").fetchall()]
        
        # Create attachment records
        for form_id in form_ids:
            cursor.execute('''
            INSERT INTO attachments (form_id, file_path, file_name, file_type, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (form_id, f'/path/to/attachment_{form_id}.txt', f'attachment_{form_id}.txt', 
                  'text/plain', 1024, datetime.now().isoformat()))
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"Test database created with {len(form_ids)} forms and {len(form_ids)} attachments")
        return True
        
    except Exception as e:
        print(f"Error creating test database: {e}")
        return False


def verify_migration(db_path):
    """
    Verify migration was applied correctly.
    
    Args:
        db_path: Path to the database
        
    Returns:
        True if migration was verified, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if updated_at column exists
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col[1] for col in cursor.fetchall()]
        has_column = 'updated_at' in columns
        
        # Count attachments
        count = cursor.execute("SELECT COUNT(*) FROM attachments").fetchone()[0]
        
        # Check if updated_at values are set
        if has_column:
            null_count = cursor.execute(
                "SELECT COUNT(*) FROM attachments WHERE updated_at IS NULL"
            ).fetchone()[0]
            
            print(f"Migration verification:")
            print(f"- updated_at column exists: {has_column}")
            print(f"- Total attachments: {count}")
            print(f"- Attachments with NULL updated_at: {null_count}")
            print(f"- Verification result: {'PASSED' if null_count == 0 else 'FAILED'}")
            
            conn.close()
            return null_count == 0
        else:
            print(f"Migration verification:")
            print(f"- updated_at column exists: {has_column}")
            print(f"- Verification result: FAILED")
            
            conn.close()
            return False
            
    except Exception as e:
        print(f"Error verifying migration: {e}")
        return False


def main():
    """Run the demonstration script."""
    parser = argparse.ArgumentParser(description='Demonstrate attachment schema migration')
    parser.add_argument('--db-path', type=str, 
                        help='Path to use for the test database (default: temporary file)')
    parser.add_argument('--keep', action='store_true',
                        help='Keep the test database after completion')
    
    args = parser.parse_args()
    
    # Create a temporary database if path not specified
    if args.db_path:
        db_path = args.db_path
        is_temp = False
    else:
        fd, db_path = tempfile.mkstemp(suffix='.db', prefix='radioforms_test_')
        os.close(fd)
        is_temp = True
    
    try:
        # Create the test database
        if not create_test_db(db_path):
            print("Failed to create test database.")
            return 1
        
        # Verify initial state
        print("\nInitial database state:")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"- Attachment table columns: {', '.join(columns)}")
        print(f"- updated_at column exists: {'updated_at' in columns}")
        conn.close()
        
        # Run the migration
        print("\nRunning migration...")
        success = run_migration(db_path)
        
        if success:
            print("Migration completed successfully!")
        else:
            print("Migration failed.")
            return 1
        
        # Verify the migration
        print("\nVerifying migration results:")
        verify_migration(db_path)
        
        # Show some data after migration
        print("\nAttachment data after migration:")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, form_id, file_name, created_at, updated_at FROM attachments")
        rows = cursor.fetchall()
        
        for row in rows:
            print(f"Attachment {row[0]} (form {row[1]}): {row[2]}")
            print(f"  Created: {row[3]}")
            print(f"  Updated: {row[4]}")
            
        conn.close()
        
        print("\nDemonstration completed successfully!")
        
    finally:
        # Clean up the temporary database if not keeping it
        if is_temp and not args.keep and os.path.exists(db_path):
            os.unlink(db_path)
            print(f"Temporary database removed: {db_path}")
        elif args.keep:
            print(f"Test database kept at: {db_path}")


if __name__ == "__main__":
    main()
