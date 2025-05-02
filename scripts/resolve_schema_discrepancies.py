#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Schema Discrepancy Resolution Script.

This script identifies and fixes all database schema discrepancies that are
causing integration issues between the form models, form registry, and DAO layers.
It builds upon the form_schema_update migration to ensure full compatibility.
"""

import sys
import os
import logging
import sqlite3
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import RadioForms modules
from radioforms.database.db_manager import DBManager


# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_current_schema(db_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get the current database schema.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        Dictionary of table names and their column definitions
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    
    # Get schema for each table
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [dict(row) for row in cursor.fetchall()]
        schema[table] = columns
        
    conn.close()
    return schema


def get_expected_schema() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get the expected database schema for the application.
    
    Returns:
        Dictionary of table names and their expected column definitions
    """
    # Define the expected schema
    schema = {
        "forms": [
            {"name": "id", "type": "INTEGER", "pk": 1, "notnull": 0},
            {"name": "form_id", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "incident_id", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "op_period_id", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "form_type", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "title", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "creator_id", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "status", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "state", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "data", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "created_at", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "updated_at", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "created_by", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "updated_by", "type": "TEXT", "pk": 0, "notnull": 0},
        ],
        "form_versions": [
            {"name": "id", "type": "INTEGER", "pk": 1, "notnull": 0},
            {"name": "form_id", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "version_number", "type": "INTEGER", "pk": 0, "notnull": 1},
            {"name": "version_id", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "content", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "created_by", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "created_at", "type": "TEXT", "pk": 0, "notnull": 1},
        ],
        "attachments": [
            {"name": "attachment_id", "type": "TEXT", "pk": 1, "notnull": 1},
            {"name": "form_id", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "filename", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "content_type", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "size", "type": "INTEGER", "pk": 0, "notnull": 1},
            {"name": "path", "type": "TEXT", "pk": 0, "notnull": 1},
            {"name": "description", "type": "TEXT", "pk": 0, "notnull": 0},
            {"name": "created_at", "type": "TIMESTAMP", "pk": 0, "notnull": 1},
            {"name": "updated_at", "type": "TIMESTAMP", "pk": 0, "notnull": 1},
        ],
    }
    
    return schema


def compare_schemas(current: Dict[str, List[Dict[str, Any]]], 
                   expected: Dict[str, List[Dict[str, Any]]]) -> Tuple[
                       List[str],                 # Missing tables
                       Dict[str, List[str]],      # Tables with missing columns
                       Dict[str, List[str]],      # Tables with differing columns
                       Dict[str, List[Dict[str, Any]]]  # Discrepancies
                   ]:
    """
    Compare the current schema with the expected schema.
    
    Args:
        current: Current database schema
        expected: Expected database schema
        
    Returns:
        Tuple of:
            - List of missing tables
            - Dictionary of tables with missing columns
            - Dictionary of tables with differing columns
            - Dictionary of tables with detailed discrepancies
    """
    missing_tables = []
    missing_columns = {}
    differing_columns = {}
    discrepancies = {}
    
    # Check for missing tables
    for table in expected:
        if table not in current:
            missing_tables.append(table)
        else:
            # Check for missing columns
            current_cols = {col['name']: col for col in current[table]}
            expected_cols = {col['name']: col for col in expected[table]}
            
            missing_cols = []
            differing_cols = []
            table_discrepancies = []
            
            for col_name, col_def in expected_cols.items():
                if col_name not in current_cols:
                    missing_cols.append(col_name)
                    table_discrepancies.append({
                        'type': 'missing_column',
                        'column': col_name,
                        'expected': col_def
                    })
                else:
                    # Compare column definitions
                    current_col = current_cols[col_name]
                    if current_col['type'] != col_def['type'] or current_col['pk'] != col_def['pk']:
                        differing_cols.append(col_name)
                        table_discrepancies.append({
                            'type': 'differing_column',
                            'column': col_name,
                            'current': current_col,
                            'expected': col_def
                        })
            
            if missing_cols:
                missing_columns[table] = missing_cols
                
            if differing_cols:
                differing_columns[table] = differing_cols
                
            if table_discrepancies:
                discrepancies[table] = table_discrepancies
    
    return missing_tables, missing_columns, differing_columns, discrepancies


def fix_schema_discrepancies(db_path: str, discrepancies: Dict[str, List[Dict[str, Any]]]) -> bool:
    """
    Fix schema discrepancies.
    
    Args:
        db_path: Path to the database file
        discrepancies: Dictionary of tables with their discrepancies
        
    Returns:
        True if fixes were applied, False otherwise
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Fix each table
        for table, issues in discrepancies.items():
            for issue in issues:
                if issue['type'] == 'missing_column':
                    # Add missing column
                    col_def = issue['expected']
                    col_name = col_def['name']
                    col_type = col_def['type']
                    
                    # Build SQL for column definition
                    sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                    
                    if col_def.get('notnull', 0) == 1:
                        # SQLite doesn't support NOT NULL in ALTER TABLE without a default value
                        if col_type == 'TEXT':
                            sql += " DEFAULT ''"
                        elif col_type == 'INTEGER':
                            sql += " DEFAULT 0"
                        elif col_type == 'REAL':
                            sql += " DEFAULT 0.0"
                        elif col_type == 'TIMESTAMP':
                            sql += " DEFAULT CURRENT_TIMESTAMP"
                    
                    logger.info(f"Adding column {col_name} to {table}")
                    cursor.execute(sql)
                    
                elif issue['type'] == 'differing_column':
                    # Handle differing column - this is more complex in SQLite
                    # as it doesn't support ALTER COLUMN directly
                    col_name = issue['column']
                    logger.info(f"Column {col_name} in {table} differs, creating backup and new table")
                    
                    # Rename the existing table
                    cursor.execute(f"ALTER TABLE {table} RENAME TO {table}_old")
                    
                    # Get the full schema for the table
                    current_schema = get_current_schema(db_path)
                    if f"{table}_old" in current_schema:
                        old_cols = current_schema[f"{table}_old"]
                        
                        # Create new table with correct schema
                        expected_schema = get_expected_schema()
                        expected_cols = expected_schema.get(table, [])
                        
                        # Build CREATE TABLE statement
                        create_sql = f"CREATE TABLE {table} (\n"
                        
                        # Add columns
                        col_defs = []
                        for col in expected_cols:
                            col_def = f"{col['name']} {col['type']}"
                            
                            if col.get('pk', 0) == 1:
                                col_def += " PRIMARY KEY"
                            
                            if col.get('notnull', 0) == 1:
                                col_def += " NOT NULL"
                                
                            col_defs.append(col_def)
                            
                        create_sql += ",\n".join(col_defs)
                        create_sql += "\n)"
                        
                        # Create the new table
                        cursor.execute(create_sql)
                        
                        # Copy data from old table to new table
                        # We need to map old column names to new column names
                        old_col_names = [col['name'] for col in old_cols]
                        expected_col_names = [col['name'] for col in expected_cols]
                        
                        # Find common columns
                        common_cols = [col for col in old_col_names if col in expected_col_names]
                        
                        # Build INSERT statement
                        insert_sql = f"INSERT INTO {table} ({', '.join(common_cols)}) "
                        insert_sql += f"SELECT {', '.join(common_cols)} FROM {table}_old"
                        
                        # Copy data
                        cursor.execute(insert_sql)
                        
                        # Drop old table
                        cursor.execute(f"DROP TABLE {table}_old")
                        
        # Commit the transaction
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Failed to fix schema discrepancies: {e}")
        conn.rollback()
        conn.close()
        return False


def create_missing_tables(db_path: str, missing_tables: List[str]) -> bool:
    """
    Create missing tables.
    
    Args:
        db_path: Path to the database file
        missing_tables: List of missing table names
        
    Returns:
        True if tables were created, False otherwise
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Get expected schema
        expected_schema = get_expected_schema()
        
        # Create each missing table
        for table in missing_tables:
            if table in expected_schema:
                expected_cols = expected_schema[table]
                
                # Build CREATE TABLE statement
                create_sql = f"CREATE TABLE {table} (\n"
                
                # Add columns
                col_defs = []
                for col in expected_cols:
                    col_def = f"{col['name']} {col['type']}"
                    
                    if col.get('pk', 0) == 1:
                        col_def += " PRIMARY KEY"
                    
                    if col.get('notnull', 0) == 1:
                        col_def += " NOT NULL"
                        
                    col_defs.append(col_def)
                    
                create_sql += ",\n".join(col_defs)
                create_sql += "\n)"
                
                # Create the table
                logger.info(f"Creating table {table}")
                cursor.execute(create_sql)
                
        # Commit the transaction
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Failed to create missing tables: {e}")
        conn.rollback()
        conn.close()
        return False


def update_schema_version(db_path: str, version: int = 4, description: str = None) -> bool:
    """
    Update the schema version.
    
    Args:
        db_path: Path to the database file
        version: New schema version
        description: Optional description of the changes
        
    Returns:
        True if version was updated, False otherwise
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Ensure schema_version table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL,
                description TEXT
            )
        """)
        
        # Insert new version
        desc = description or "Fixed schema discrepancies"
        cursor.execute(
            "INSERT INTO schema_version (version, applied_at, description) VALUES (?, datetime('now'), ?)",
            (version, desc)
        )
        
        # Commit the transaction
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Failed to update schema version: {e}")
        conn.rollback()
        conn.close()
        return False


def fix_all_schema_issues(db_path: str) -> bool:
    """
    Fix all schema issues in the database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        True if all issues were fixed, False otherwise
    """
    logger.info(f"Checking database schema for {db_path}")
    
    # Get current and expected schemas
    current_schema = get_current_schema(db_path)
    expected_schema = get_expected_schema()
    
    # Compare schemas
    missing_tables, missing_columns, differing_columns, discrepancies = compare_schemas(
        current_schema, expected_schema
    )
    
    if not missing_tables and not discrepancies:
        logger.info("No schema issues found")
        return True
        
    # Report issues
    if missing_tables:
        logger.info(f"Missing tables: {', '.join(missing_tables)}")
        
    for table, cols in missing_columns.items():
        logger.info(f"Table {table} missing columns: {', '.join(cols)}")
        
    for table, cols in differing_columns.items():
        logger.info(f"Table {table} has differing columns: {', '.join(cols)}")
    
    # Fix issues
    success = True
    
    if missing_tables:
        logger.info("Creating missing tables...")
        if not create_missing_tables(db_path, missing_tables):
            logger.error("Failed to create missing tables")
            success = False
    
    if discrepancies:
        logger.info("Fixing schema discrepancies...")
        if not fix_schema_discrepancies(db_path, discrepancies):
            logger.error("Failed to fix schema discrepancies")
            success = False
    
    if success:
        logger.info("Updating schema version...")
        if not update_schema_version(db_path, 4, "Fixed schema discrepancies"):
            logger.error("Failed to update schema version")
            success = False
    
    return success


def main():
    """Run the script."""
    parser = argparse.ArgumentParser(description="Fix database schema discrepancies")
    parser.add_argument('--db-path', type=str, help='Path to the database file')
    parser.add_argument('--force', action='store_true', help='Force schema update even if no issues are found')
    args = parser.parse_args()
    
    # Determine database path
    db_path = args.db_path
    if not db_path:
        # Check environment variable
        db_path = os.environ.get('RADIOFORMS_DB_PATH')
        
        if not db_path:
            # Use default location
            config_dir = os.environ.get('RADIOFORMS_CONFIG_DIR')
            if not config_dir:
                config_dir = os.path.join(os.path.expanduser('~'), '.radioforms')
                
            db_path = os.path.join(config_dir, 'radioforms.db')
            
    logger.info(f"Using database at {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        logger.error(f"Database file {db_path} does not exist")
        return 1
        
    # Fix schema issues
    if fix_all_schema_issues(db_path) or args.force:
        logger.info("Schema discrepancies fixed successfully")
        return 0
    else:
        logger.error("Failed to fix schema discrepancies")
        return 1


if __name__ == "__main__":
    sys.exit(main())
