#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to run the migration that adds updated_at column to attachments table.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from radioforms.database.migrations.add_updated_at_to_attachments import run_migration
from radioforms.database.db_manager import DatabaseManager
from radioforms.config.app_config import AppConfig


def get_database_path(custom_path=None):
    """
    Get the database path from config or custom path.
    
    Args:
        custom_path: Optional path to override the default
        
    Returns:
        Path to the database
    """
    if custom_path:
        return custom_path
        
    # Use the configuration to get the default database path
    config = AppConfig()
    return config.get('database', 'path')


def main():
    """Run the migration script."""
    parser = argparse.ArgumentParser(description='Run migration to add updated_at column to attachments table')
    parser.add_argument('--db-path', type=str, 
                        help='Path to the SQLite database file (default: from app config)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Check if migration is needed without making changes')
    
    args = parser.parse_args()
    db_path = get_database_path(args.db_path)
    
    print(f"Using database at: {db_path}")
    
    if args.dry_run:
        print("Performing dry run...")
        # Check if column exists
        if not os.path.exists(db_path):
            print("Database file not found.")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
        
        if 'updated_at' in columns:
            print("Migration is NOT needed: 'updated_at' column already exists.")
        else:
            print("Migration IS needed: 'updated_at' column does not exist.")
        return
    
    # Run the actual migration
    success = run_migration(db_path)
    
    if success:
        print("Migration completed successfully!")
        
        # Verify the migration
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
        
        if 'updated_at' in columns:
            print("Verification successful: 'updated_at' column exists in the attachments table.")
        else:
            print("Verification failed: 'updated_at' column not found after migration.")
    else:
        print("Migration failed. Please check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    import sqlite3
    main()
