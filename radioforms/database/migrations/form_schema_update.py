#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Migration script to update the forms table schema.

This migration ensures the forms table has the proper columns needed by
the enhanced form models and form model registry, fixing any schema discrepancies
that might be causing errors like "no such column: id".
"""

import os
import sqlite3
from typing import Tuple


def update_form_schema(db_path: str) -> Tuple[bool, str]:
    """
    Update the forms table schema to fix discrepancies.
    
    Args:
        db_path: Path to the SQLite database
        
    Returns:
        Tuple containing:
            - Success flag (True if migration was successful)
            - Message describing the outcome
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Always recreate the forms table to ensure proper structure
        conn.execute("DROP TABLE IF EXISTS forms")
        conn.execute("""
        CREATE TABLE forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id TEXT UNIQUE NOT NULL,
            incident_id TEXT,
            op_period_id TEXT,
            form_type TEXT NOT NULL,
            title TEXT,
            creator_id TEXT,
            status TEXT DEFAULT 'draft',
            state TEXT DEFAULT 'draft',
            data TEXT,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT,
            updated_by TEXT
        )
        """)
        
        # Always recreate the form_versions table
        conn.execute("DROP TABLE IF EXISTS form_versions")
        conn.execute("""
        CREATE TABLE form_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id TEXT NOT NULL,
            version_number INTEGER NOT NULL,
            version_id TEXT,
            content TEXT,
            created_by TEXT,
            created_at TEXT,
            UNIQUE(form_id, version_number)
        )
        """)
        
        # Create index on form_id
        conn.execute("CREATE INDEX idx_forms_form_id ON forms(form_id)")
        
        # Updates were definitely made
        updates_made = True
            
        conn.commit()
        conn.close()
        
        if updates_made:
            return True, "Updated forms table schema successfully"
        else:
            return True, "No schema updates needed for forms table"
            
    except Exception as e:
        return False, f"Error updating forms table schema: {str(e)}"


def run_migration(db_path: str) -> Tuple[bool, str]:
    """
    Run the migration to update the forms table schema.
    
    Args:
        db_path: Path to the SQLite database
        
    Returns:
        Tuple containing:
            - Success flag (True if migration was successful)
            - Message describing the outcome
    """
    return update_form_schema(db_path)


if __name__ == "__main__":
    # Get the database path from environment or use default
    db_path = os.environ.get("RADIOFORMS_DB_PATH", "radioforms.db")
    
    success, message = run_migration(db_path)
    print(f"Migration {'succeeded' if success else 'failed'}: {message}")
