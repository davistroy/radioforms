#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Schema Migration Script.

This script creates a proper schema migration to ensure all column names
in the database match what the application code expects.
"""

import sys
import os
import logging
import tempfile
import sqlite3
from pathlib import Path

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_expected_schema():
    """
    Define the expected schema for all tables.
    
    Returns:
        Dictionary with table names as keys and a list of column definitions as values
    """
    return {
        'forms': [
            'form_id TEXT PRIMARY KEY',
            'incident_id TEXT',
            'op_period_id TEXT',
            'form_type TEXT NOT NULL',
            'state TEXT NOT NULL DEFAULT "draft"',
            'data TEXT',
            'created_at TEXT NOT NULL',
            'updated_at TEXT NOT NULL',
            'created_by TEXT',
            'updated_by TEXT',
            'title TEXT'
        ],
        'form_versions': [
            'version_id TEXT PRIMARY KEY',
            'form_id TEXT NOT NULL',
            'version INTEGER NOT NULL',
            'content TEXT NOT NULL',
            'created_at TEXT NOT NULL',
            'comment TEXT',
            'user_id TEXT'
        ],
        'incidents': [
            'incident_id TEXT PRIMARY KEY',
            'name TEXT NOT NULL',
            'description TEXT',
            'status TEXT NOT NULL DEFAULT "active"',
            'created_at TEXT NOT NULL',
            'updated_at TEXT NOT NULL'
        ],
        'operational_periods': [
            'op_period_id TEXT PRIMARY KEY',
            'incident_id TEXT NOT NULL',
            'start_time TEXT NOT NULL',
            'end_time TEXT NOT NULL',
            'name TEXT',
            'created_at TEXT NOT NULL',
            'updated_at TEXT NOT NULL'
        ],
        'attachments': [
            'attachment_id TEXT PRIMARY KEY',
            'form_id TEXT NOT NULL',
            'filename TEXT NOT NULL',
            'file_path TEXT NOT NULL',
            'file_size INTEGER',
            'mime_type TEXT',
            'upload_time TEXT NOT NULL',
            'uploader_id TEXT',
            'description TEXT'
        ],
        'users': [
            'user_id TEXT PRIMARY KEY',
            'username TEXT NOT NULL UNIQUE',
            'email TEXT',
            'full_name TEXT',
            'password_hash TEXT',
            'role TEXT NOT NULL DEFAULT "user"',
            'created_at TEXT NOT NULL',
            'last_login TEXT'
        ]
    }


def check_schema(db_path):
    """
    Check current schema against expected schema.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        Dictionary with tables and missing/different columns
    """
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get expected schema
    expected_schema = get_expected_schema()
    
    # Check each table
    differences = {}
    
    for table_name, expected_columns in expected_schema.items():
        # Check if table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if not cursor.fetchone():
            differences[table_name] = {"missing_table": True}
            continue
            
        # Get current columns
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        current_columns = {row['name']: row for row in cursor.fetchall()}
        
        # Check columns
        column_issues = []
        for column_def in expected_columns:
            # Extract column name and definition
            parts = column_def.split(' ', 1)
            column_name = parts[0]
            column_type = parts[1] if len(parts) > 1 else ""
            
            if column_name not in current_columns:
                column_issues.append(f"Missing column: {column_name} {column_type}")
        
        if column_issues:
            differences[table_name] = {"issues": column_issues}
    
    # Close connection
    conn.close()
    
    return differences


def create_migration_sql(differences):
    """
    Create SQL migration statements from schema differences.
    
    Args:
        differences: Dictionary with tables and missing/different columns
        
    Returns:
        List of SQL statements to fix the schema
    """
    # Get expected schema
    expected_schema = get_expected_schema()
    
    # Create SQL statements
    sql_statements = []
    
    for table_name, issues in differences.items():
        if "missing_table" in issues:
            # Create table
            columns = ", ".join(expected_schema[table_name])
            sql_statements.append(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});")
        elif "issues" in issues:
            # Add missing columns
            for issue in issues["issues"]:
                if issue.startswith("Missing column:"):
                    column_def = issue.replace("Missing column: ", "")
                    sql_statements.append(f"ALTER TABLE {table_name} ADD COLUMN {column_def};")
    
    return sql_statements


def apply_migration(db_path, sql_statements):
    """
    Apply migration SQL statements to the database.
    
    Args:
        db_path: Path to the database file
        sql_statements: List of SQL statements to execute
        
    Returns:
        True if successful, False otherwise
    """
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    try:
        # Begin transaction
        conn.execute("BEGIN TRANSACTION;")
        
        # Execute each statement
        for statement in sql_statements:
            logger.info(f"Executing: {statement}")
            conn.execute(statement)
        
        # Commit transaction
        conn.execute("COMMIT;")
        
        # Close connection
        conn.close()
        
        return True
    except Exception as e:
        # Rollback on error
        conn.execute("ROLLBACK;")
        
        # Close connection
        conn.close()
        
        logger.error(f"Migration failed: {e}")
        return False


def migrate_test_db():
    """
    Create a temporary test database and perform migration.
    
    Returns:
        Path to the migrated database file
    """
    # Create a temporary database
    db_dir = tempfile.mkdtemp()
    db_path = os.path.join(db_dir, "test_migrated.db")
    
    # Initialize database with basic schema
    logger.info(f"Creating test database at {db_path}")
    from radioforms.database.db_manager import DBManager
    db_manager = DBManager(db_path)
    db_manager.init_db()
    db_manager.close()
    
    # Check schema differences
    differences = check_schema(db_path)
    
    if not differences:
        logger.info("No schema differences found")
        return db_path
    
    # Generate and apply migration
    logger.info(f"Found schema differences: {differences}")
    sql_statements = create_migration_sql(differences)
    
    if not sql_statements:
        logger.info("No migration statements generated")
        return db_path
    
    logger.info(f"Applying migration with {len(sql_statements)} statements")
    success = apply_migration(db_path, sql_statements)
    
    if success:
        logger.info("Migration applied successfully")
    else:
        logger.warning("Migration failed")
    
    return db_path


def migrate_db(db_path):
    """
    Migrate the specified database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        True if successful, False otherwise
    """
    # Check if database exists
    if not os.path.isfile(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False
    
    # Create backup first
    backup_path = f"{db_path}.bak.{int(os.path.getmtime(db_path))}"
    logger.info(f"Creating backup at {backup_path}")
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False
    
    # Check schema differences
    differences = check_schema(db_path)
    
    if not differences:
        logger.info("No schema differences found")
        return True
    
    # Generate and apply migration
    logger.info(f"Found schema differences: {differences}")
    sql_statements = create_migration_sql(differences)
    
    if not sql_statements:
        logger.info("No migration statements generated")
        return True
    
    logger.info(f"Applying migration with {len(sql_statements)} statements")
    success = apply_migration(db_path, sql_statements)
    
    if success:
        logger.info("Migration applied successfully")
    else:
        logger.warning("Migration failed")
    
    return success


def main():
    """Run the script."""
    logger.info("Starting schema migration script")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        success = migrate_db(db_path)
    else:
        # No arguments, run on test database
        db_path = migrate_test_db()
        success = db_path is not None
    
    if success:
        logger.info(f"Schema migration completed successfully for {db_path}")
        return 0
    else:
        logger.error("Schema migration failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
