#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database Manager for RadioForms.

This module provides the database manager for RadioForms, which handles
database connections, schema initialization, migrations, and provides
utility functions for database operations.
"""

import os
import sys
import sqlite3
import logging
import datetime
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple


class DBManager:
    """
    Database Manager for RadioForms.
    
    This class handles database connections, schema initialization, migrations,
    and provides utility functions for database operations.
    """
    
    # Schema version
    SCHEMA_VERSION = 3
    
    # Schema creation statements
    SCHEMA_STATEMENTS = [
        # Version tracking table
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP NOT NULL,
            description TEXT
        )
        """,
        
        # Settings table
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """,
        
        # User table
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            callsign TEXT,
            position TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """,
        
        # Incident table
        """
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            incident_number TEXT,
            type TEXT,
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """,
        
        # Operational period table
        """
        CREATE TABLE IF NOT EXISTS operational_periods (
            op_period_id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            number INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id) ON DELETE CASCADE
        )
        """,
        
        # Form table
        """
        CREATE TABLE IF NOT EXISTS forms (
            form_id TEXT PRIMARY KEY,
            incident_id TEXT,
            op_period_id TEXT,
            form_type TEXT NOT NULL,
            state TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            created_by TEXT,
            updated_by TEXT,
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id) ON DELETE CASCADE,
            FOREIGN KEY (op_period_id) REFERENCES operational_periods (op_period_id) ON DELETE SET NULL
        )
        """,
        
        # Form version table for history tracking
        """
        CREATE TABLE IF NOT EXISTS form_versions (
            version_id TEXT PRIMARY KEY,
            form_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            created_by TEXT,
            FOREIGN KEY (form_id) REFERENCES forms (form_id) ON DELETE CASCADE
        )
        """,
        
        # Attachment table
        """
        CREATE TABLE IF NOT EXISTS attachments (
            attachment_id TEXT PRIMARY KEY,
            form_id TEXT,
            filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            size INTEGER NOT NULL,
            path TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            FOREIGN KEY (form_id) REFERENCES forms (form_id) ON DELETE CASCADE
        )
        """
    ]
    
    def __init__(self, db_path: str):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = db_path
        self._conn = None
        self._logger = logging.getLogger(__name__)
        
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        
    def connect(self) -> sqlite3.Connection:
        """
        Get a database connection.
        
        Returns:
            SQLite database connection
        """
        if self._conn is None:
            try:
                # Connect to the database
                self._conn = sqlite3.connect(self._db_path)
                
                # Enable foreign keys
                self._conn.execute("PRAGMA foreign_keys = ON")
                
                # Configure connection for dictionary rows
                self._conn.row_factory = sqlite3.Row
                
                self._logger.debug(f"Connected to database at {self._db_path}")
            except Exception as e:
                self._logger.error(f"Failed to connect to database: {e}")
                raise
                
        return self._conn
        
    def close(self):
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            self._logger.debug("Database connection closed")
            
    def init_db(self):
        """
        Initialize the database schema.
        
        This method creates the necessary tables if they don't exist
        and runs migrations to update the schema to the latest version.
        """
        try:
            conn = self.connect()
            
            # Create tables
            for statement in self.SCHEMA_STATEMENTS:
                conn.execute(statement)
                
            # Check schema version
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
            has_version_table = cursor.fetchone() is not None
            
            if has_version_table:
                # Get current schema version
                cursor = conn.execute("SELECT MAX(version) AS version FROM schema_version")
                row = cursor.fetchone()
                current_version = row['version'] if row and row['version'] is not None else 0
            else:
                current_version = 0
                
            # Run migrations if needed
            if current_version < self.SCHEMA_VERSION:
                self._run_migrations(current_version)
                
            # Commit changes
            conn.commit()
            
            self._logger.info(f"Database initialized with schema version {self.SCHEMA_VERSION}")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize database: {e}")
            if self._conn:
                self._conn.rollback()
            raise
            
    def _run_migrations(self, current_version: int):
        """
        Run database migrations to update schema.
        
        Args:
            current_version: Current schema version
        """
        conn = self.connect()
        
        try:
            # Run migrations from current_version+1 to SCHEMA_VERSION
            for version in range(current_version + 1, self.SCHEMA_VERSION + 1):
                self._logger.info(f"Running migration to version {version}")
                
                # Run migration method for this version
                migration_method = getattr(self, f"_migrate_to_v{version}", None)
                description = ""
                
                if migration_method:
                    description = migration_method(conn)
                else:
                    self._logger.warning(f"No migration method found for version {version}")
                    
                # Record migration
                conn.execute(
                    "INSERT INTO schema_version (version, applied_at, description) VALUES (?, ?, ?)",
                    (version, datetime.datetime.now().isoformat(), description)
                )
                
            # Commit changes
            conn.commit()
            
        except Exception as e:
            self._logger.error(f"Migration failed: {e}")
            conn.rollback()
            raise
            
    def _migrate_to_v1(self, conn: sqlite3.Connection) -> str:
        """
        Migrate database to version 1.
        
        Args:
            conn: Database connection
            
        Returns:
            Migration description
        """
        # This is a placeholder for a real migration
        return "Initial schema"
        
    def _migrate_to_v2(self, conn: sqlite3.Connection) -> str:
        """
        Migrate database to version 2.
        
        Args:
            conn: Database connection
            
        Returns:
            Migration description
        """
        # Add updated_at column to attachments table if it doesn't exist
        try:
            conn.execute("SELECT updated_at FROM attachments LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE attachments ADD COLUMN updated_at TIMESTAMP")
            
        return "Add updated_at to attachments table"
    
    def _migrate_to_v3(self, conn: sqlite3.Connection) -> str:
        """
        Migrate database to version 3.
        
        This migration ensures the forms table has the proper columns needed by
        the enhanced form models and form model registry, fixing schema discrepancies.
        
        Args:
            conn: Database connection
            
        Returns:
            Migration description
        """
        try:
            # Do not close the connection in the migration function
            # Create forms table if it doesn't exist
            conn.execute("""
            CREATE TABLE IF NOT EXISTS forms (
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
            
            # Get column names
            cursor = conn.execute("PRAGMA table_info(forms)")
            columns = [column['name'] for column in cursor.fetchall()]
            
            # Add form_id column if missing
            if 'form_id' not in columns:
                conn.execute("ALTER TABLE forms ADD COLUMN form_id TEXT UNIQUE")
                
            # Add data column if missing
            if 'data' not in columns:
                conn.execute("ALTER TABLE forms ADD COLUMN data TEXT")
                
            # Add state column if missing
            if 'state' not in columns:
                conn.execute("ALTER TABLE forms ADD COLUMN state TEXT DEFAULT 'draft'")
                
            # Add title column if missing
            if 'title' not in columns:
                conn.execute("ALTER TABLE forms ADD COLUMN title TEXT")
            
            # Create form_versions table if it doesn't exist
            conn.execute("""
            CREATE TABLE IF NOT EXISTS form_versions (
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
            
            conn.commit()
            return "Updated forms table schema to fix discrepancies"
            
        except Exception as e:
            self._logger.error(f"Error updating forms table schema: {e}")
            raise
        
    def create_backup(self) -> Optional[str]:
        """
        Create a backup of the database.
        
        Returns:
            Path to the backup file, or None if backup failed
        """
        if not os.path.exists(self._db_path):
            self._logger.warning("Cannot create backup: database file does not exist")
            return None
            
        try:
            # Create backup file name with timestamp
            backup_dir = os.path.join(os.path.dirname(self._db_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"radioforms_{timestamp}.db")
            
            # Close connection to allow backup
            self.close()
            
            # Copy database file
            shutil.copy2(self._db_path, backup_path)
            
            self._logger.info(f"Database backup created at {backup_path}")
            return backup_path
            
        except Exception as e:
            self._logger.error(f"Failed to create backup: {e}")
            return None
            
    def execute(self, query: str, params: Union[Tuple, Dict] = (), commit: bool = False) -> sqlite3.Cursor:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query
            params: Query parameters
            commit: Whether to commit the transaction
            
        Returns:
            SQLite cursor
        """
        conn = self.connect()
        
        try:
            cursor = conn.execute(query, params)
            
            if commit:
                conn.commit()
                
            return cursor
            
        except Exception as e:
            self._logger.error(f"Query execution failed: {e}")
            if commit:
                conn.rollback()
            raise
            
    def execute_many(self, query: str, params_list: List[Union[Tuple, Dict]], commit: bool = False) -> sqlite3.Cursor:
        """
        Execute a SQL query with multiple parameter sets.
        
        Args:
            query: SQL query
            params_list: List of parameter sets
            commit: Whether to commit the transaction
            
        Returns:
            SQLite cursor
        """
        conn = self.connect()
        
        try:
            cursor = conn.executemany(query, params_list)
            
            if commit:
                conn.commit()
                
            return cursor
            
        except Exception as e:
            self._logger.error(f"Bulk query execution failed: {e}")
            if commit:
                conn.rollback()
            raise
            
    def begin_transaction(self):
        """Begin a transaction."""
        conn = self.connect()
        conn.execute("BEGIN TRANSACTION")
        
    def commit(self):
        """Commit the current transaction."""
        if self._conn is not None:
            self._conn.commit()
            
    def rollback(self):
        """Roll back the current transaction."""
        if self._conn is not None:
            self._conn.rollback()
            
    def query_to_dict(self, query: str, params: Union[Tuple, Dict] = ()) -> List[Dict[str, Any]]:
        """
        Execute a query and return the results as a list of dictionaries.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of row dictionaries
        """
        cursor = self.execute(query, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def get_schema_version(self) -> int:
        """
        Get the current schema version.
        
        Returns:
            Current schema version
        """
        try:
            conn = self.connect()
            cursor = conn.execute("SELECT MAX(version) AS version FROM schema_version")
            row = cursor.fetchone()
            return row['version'] if row and row['version'] is not None else 0
        except Exception:
            return 0


# Create a DatabaseManager class reference for backwards compatibility
# with existing code that expects it to be imported from db_manager
class DatabaseManager(DBManager):
    """
    Alias for DBManager class.
    
    This class is provided for backwards compatibility with code that
    imports DatabaseManager from radioforms.database.db_manager.
    """
    pass
