#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Schema Manager.

This module provides a robust schema management system for the RadioForms database.
It tracks schema versions, applies migrations, and ensures database consistency.
"""

import os
import sqlite3
import json
import logging
import datetime
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Tuple

logger = logging.getLogger(__name__)


class Migration:
    """
    A database schema migration.
    
    This class represents a single migration that can be applied to the database
    to update its schema from one version to another.
    """
    
    def __init__(self, version: int, description: str, sql: List[str], 
                 pre_migrate_hook: Optional[Callable] = None, 
                 post_migrate_hook: Optional[Callable] = None):
        """
        Initialize the migration.
        
        Args:
            version: Target schema version
            description: Human-readable description of the migration
            sql: List of SQL statements to execute
            pre_migrate_hook: Optional function to call before migration
            post_migrate_hook: Optional function to call after migration
        """
        self.version = version
        self.description = description
        self.sql = sql
        self.pre_migrate_hook = pre_migrate_hook
        self.post_migrate_hook = post_migrate_hook
    
    def apply(self, conn: sqlite3.Connection) -> bool:
        """
        Apply the migration to the database.
        
        Args:
            conn: SQLite connection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Start transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Call pre-migration hook if provided
            if self.pre_migrate_hook:
                self.pre_migrate_hook(conn)
            
            # Execute SQL statements
            for statement in self.sql:
                statement = statement.strip()
                if statement:
                    conn.execute(statement)
            
            # Update schema_version table
            conn.execute(
                """
                INSERT OR REPLACE INTO schema_version (
                    version, applied_at, description
                ) VALUES (?, ?, ?)
                """,
                (self.version, self._now(), self.description)
            )
            
            # Call post-migration hook if provided
            if self.post_migrate_hook:
                self.post_migrate_hook(conn)
            
            # Commit transaction
            conn.execute("COMMIT")
            
            logger.info(f"Migration to version {self.version} applied successfully")
            return True
            
        except Exception as e:
            # Rollback transaction on error
            conn.execute("ROLLBACK")
            
            logger.error(f"Migration to version {self.version} failed: {e}")
            return False
    
    def _now(self) -> str:
        """
        Get the current timestamp as a string.
        
        Returns:
            ISO format timestamp string
        """
        return datetime.datetime.now().replace(microsecond=0).isoformat()


class SchemaManager:
    """
    Database schema manager.
    
    This class manages the database schema, tracking versions and applying migrations
    to ensure the database is at the correct version.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the schema manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.migrations = []
        self.initialized = False
        
        # Register migrations
        self._register_migrations()
    
    def initialize(self) -> bool:
        """
        Initialize the schema manager.
        
        Creates the schema_version table if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._connect()
            
            # Create schema_version table if it doesn't exist
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL,
                    description TEXT
                )
                """
            )
            
            conn.commit()
            conn.close()
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize schema manager: {e}")
            return False
    
    def get_current_version(self) -> int:
        """
        Get the current schema version from the database.
        
        Returns:
            Current schema version, or 0 if no version found
        """
        try:
            conn = self._connect()
            
            # Check if schema_version table exists
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='schema_version'
                """
            )
            
            if not cursor.fetchone():
                conn.close()
                return 0
            
            # Get current version
            cursor = conn.execute(
                "SELECT MAX(version) FROM schema_version"
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] is not None else 0
            
        except Exception as e:
            logger.error(f"Failed to get current schema version: {e}")
            return 0
    
    def get_highest_version(self) -> int:
        """
        Get the highest available migration version.
        
        Returns:
            Highest available migration version
        """
        if not self.migrations:
            return 0
            
        return max(migration.version for migration in self.migrations)
    
    def upgrade(self, target_version: Optional[int] = None) -> bool:
        """
        Upgrade the database schema to the target version.
        
        Args:
            target_version: Target version to upgrade to, or None for latest
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized and not self.initialize():
            return False
        
        current_version = self.get_current_version()
        
        if target_version is None:
            target_version = self.get_highest_version()
        
        if current_version >= target_version:
            logger.info(f"Database already at version {current_version}, no upgrade needed")
            return True
        
        logger.info(f"Upgrading database from version {current_version} to {target_version}")
        
        # Get migrations to apply
        migrations_to_apply = [
            m for m in self.migrations
            if m.version > current_version and m.version <= target_version
        ]
        
        # Sort migrations by version
        migrations_to_apply.sort(key=lambda m: m.version)
        
        # Create backup before upgrading
        if not self._create_backup():
            logger.error("Failed to create backup, aborting upgrade")
            return False
        
        # Apply migrations
        conn = self._connect()
        
        try:
            for migration in migrations_to_apply:
                logger.info(f"Applying migration to version {migration.version}: {migration.description}")
                
                if not migration.apply(conn):
                    logger.error(f"Failed to apply migration to version {migration.version}")
                    conn.close()
                    return False
            
            conn.close()
            
            logger.info(f"Database upgraded to version {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error during schema upgrade: {e}")
            conn.close()
            return False
    
    def verify_schema(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify the database schema against the expected schema.
        
        Returns:
            Tuple of (is_valid, issues) where is_valid is True if the schema is valid,
            and issues is a dictionary containing any issues found.
        """
        try:
            conn = self._connect()
            
            # Get current tables
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
            )
            
            current_tables = {row[0] for row in cursor.fetchall()}
            
            # Get expected tables
            expected_tables = self._get_expected_tables()
            
            # Check for missing tables
            missing_tables = expected_tables.keys() - current_tables
            
            # Check columns for each table
            column_issues = {}
            
            for table in current_tables & expected_tables.keys():
                cursor = conn.execute(f"PRAGMA table_info({table})")
                current_columns = {row[1]: row for row in cursor.fetchall()}
                
                expected_columns = expected_tables[table]
                
                # Check for missing columns
                missing_columns = []
                
                for column_name, column_def in expected_columns.items():
                    if column_name not in current_columns:
                        missing_columns.append(column_name)
                
                if missing_columns:
                    column_issues[table] = missing_columns
            
            conn.close()
            
            # Build issues report
            issues = {}
            
            if missing_tables:
                issues["missing_tables"] = list(missing_tables)
                
            if column_issues:
                issues["missing_columns"] = column_issues
            
            return len(issues) == 0, issues
            
        except Exception as e:
            logger.error(f"Failed to verify schema: {e}")
            return False, {"error": str(e)}
    
    def generate_migration(self, description: str, from_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a new migration.
        
        Args:
            description: Human-readable description of the migration
            from_file: Optional path to a SQL file containing the migration statements
            
        Returns:
            Dictionary with migration details
        """
        current_version = self.get_current_version()
        new_version = current_version + 1
        
        # Get SQL statements
        sql_statements = []
        
        if from_file:
            with open(from_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('--'):
                        sql_statements.append(line)
        
        # Create migration template
        migration = {
            "version": new_version,
            "description": description,
            "sql": sql_statements,
            "created_at": datetime.datetime.now().replace(microsecond=0).isoformat()
        }
        
        return migration
    
    def _register_migrations(self):
        """
        Register all available migrations.
        """
        # Migration 1: Initial schema
        self.migrations.append(Migration(
            version=1,
            description="Initial schema",
            sql=[
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS operational_periods (
                    op_period_id TEXT PRIMARY KEY,
                    incident_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    name TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS forms (
                    form_id TEXT PRIMARY KEY,
                    incident_id TEXT,
                    op_period_id TEXT,
                    form_type TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'draft',
                    data TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT,
                    updated_by TEXT,
                    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
                    FOREIGN KEY (op_period_id) REFERENCES operational_periods(op_period_id)
                )
                """
            ]
        ))
        
        # Migration 2: Add attachments table
        self.migrations.append(Migration(
            version=2,
            description="Add attachments table",
            sql=[
                """
                CREATE TABLE IF NOT EXISTS attachments (
                    attachment_id TEXT PRIMARY KEY,
                    form_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    mime_type TEXT,
                    upload_time TEXT NOT NULL,
                    uploader_id TEXT,
                    description TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms(form_id)
                )
                """
            ]
        ))
        
        # Migration 3: Add title column to forms table
        self.migrations.append(Migration(
            version=3,
            description="Add title column to forms table",
            sql=[
                """
                ALTER TABLE forms ADD COLUMN title TEXT
                """
            ]
        ))
        
        # Migration 4: Add form versions table
        self.migrations.append(Migration(
            version=4,
            description="Add form versions table",
            sql=[
                """
                CREATE TABLE IF NOT EXISTS form_versions (
                    version_id TEXT PRIMARY KEY,
                    form_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    comment TEXT,
                    user_id TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms(form_id),
                    UNIQUE (form_id, version)
                )
                """
            ]
        ))
        
        # Migration 5: Add users table
        self.migrations.append(Migration(
            version=5,
            description="Add users table",
            sql=[
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT,
                    full_name TEXT,
                    password_hash TEXT,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
                """
            ]
        ))
    
    def _get_expected_tables(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Get the expected tables and their columns.
        
        Returns:
            Dictionary mapping table names to dictionaries of column definitions
        """
        return {
            "schema_version": {
                "version": {"type": "INTEGER", "primary_key": True},
                "applied_at": {"type": "TEXT", "not_null": True},
                "description": {"type": "TEXT"}
            },
            "incidents": {
                "incident_id": {"type": "TEXT", "primary_key": True},
                "name": {"type": "TEXT", "not_null": True},
                "description": {"type": "TEXT"},
                "status": {"type": "TEXT", "not_null": True, "default": "active"},
                "created_at": {"type": "TEXT", "not_null": True},
                "updated_at": {"type": "TEXT", "not_null": True}
            },
            "operational_periods": {
                "op_period_id": {"type": "TEXT", "primary_key": True},
                "incident_id": {"type": "TEXT", "not_null": True},
                "start_time": {"type": "TEXT", "not_null": True},
                "end_time": {"type": "TEXT", "not_null": True},
                "name": {"type": "TEXT"},
                "created_at": {"type": "TEXT", "not_null": True},
                "updated_at": {"type": "TEXT", "not_null": True}
            },
            "forms": {
                "form_id": {"type": "TEXT", "primary_key": True},
                "incident_id": {"type": "TEXT"},
                "op_period_id": {"type": "TEXT"},
                "form_type": {"type": "TEXT", "not_null": True},
                "state": {"type": "TEXT", "not_null": True, "default": "draft"},
                "data": {"type": "TEXT"},
                "created_at": {"type": "TEXT", "not_null": True},
                "updated_at": {"type": "TEXT", "not_null": True},
                "created_by": {"type": "TEXT"},
                "updated_by": {"type": "TEXT"},
                "title": {"type": "TEXT"}
            },
            "attachments": {
                "attachment_id": {"type": "TEXT", "primary_key": True},
                "form_id": {"type": "TEXT", "not_null": True},
                "filename": {"type": "TEXT", "not_null": True},
                "file_path": {"type": "TEXT", "not_null": True},
                "file_size": {"type": "INTEGER"},
                "mime_type": {"type": "TEXT"},
                "upload_time": {"type": "TEXT", "not_null": True},
                "uploader_id": {"type": "TEXT"},
                "description": {"type": "TEXT"}
            },
            "form_versions": {
                "version_id": {"type": "TEXT", "primary_key": True},
                "form_id": {"type": "TEXT", "not_null": True},
                "version": {"type": "INTEGER", "not_null": True},
                "content": {"type": "TEXT", "not_null": True},
                "created_at": {"type": "TEXT", "not_null": True},
                "comment": {"type": "TEXT"},
                "user_id": {"type": "TEXT"}
            },
            "users": {
                "user_id": {"type": "TEXT", "primary_key": True},
                "username": {"type": "TEXT", "not_null": True},
                "email": {"type": "TEXT"},
                "full_name": {"type": "TEXT"},
                "password_hash": {"type": "TEXT"},
                "role": {"type": "TEXT", "not_null": True, "default": "user"},
                "created_at": {"type": "TEXT", "not_null": True},
                "last_login": {"type": "TEXT"}
            }
        }
    
    def _connect(self) -> sqlite3.Connection:
        """
        Connect to the database.
        
        Returns:
            SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_backup(self) -> bool:
        """
        Create a backup of the database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"radioforms_{timestamp}.db")
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Database backup created at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return False


class MigrationRunner:
    """
    Migration runner for database schema updates.
    
    This utility class provides a command-line interface for managing database migrations.
    """
    
    @staticmethod
    def run():
        """
        Run the migration runner.
        """
        import argparse
        
        parser = argparse.ArgumentParser(description="Database migration runner")
        parser.add_argument("--db", help="Path to SQLite database file", required=True)
        parser.add_argument("--version", type=int, help="Target schema version (default: latest)")
        parser.add_argument("--verify", action="store_true", help="Verify database schema")
        parser.add_argument("--generate", help="Generate migration with description")
        parser.add_argument("--from-file", help="SQL file for migration generation")
        
        args = parser.parse_args()
        
        # Create schema manager
        schema_manager = SchemaManager(args.db)
        
        if args.verify:
            # Verify schema
            is_valid, issues = schema_manager.verify_schema()
            
            if is_valid:
                print("Database schema is valid")
                return 0
            else:
                print("Database schema has issues:")
                print(json.dumps(issues, indent=2))
                return 1
        
        elif args.generate:
            # Generate migration
            migration = schema_manager.generate_migration(args.generate, args.from_file)
            
            # Print migration details
            print(json.dumps(migration, indent=2))
            return 0
        
        else:
            # Run migration
            current_version = schema_manager.get_current_version()
            target_version = args.version or schema_manager.get_highest_version()
            
            print(f"Current schema version: {current_version}")
            print(f"Target schema version: {target_version}")
            
            if current_version >= target_version:
                print("No migration needed")
                return 0
            
            if schema_manager.upgrade(target_version):
                print(f"Database upgraded to version {target_version}")
                return 0
            else:
                print("Migration failed")
                return 1


def hook_example(conn: sqlite3.Connection):
    """
    Example hook function for migrations.
    
    Args:
        conn: SQLite connection
    """
    # This is just an example of what a hook function could do
    pass


if __name__ == "__main__":
    # Run migration runner
    import sys
    sys.exit(MigrationRunner.run())
