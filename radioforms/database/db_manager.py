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
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

from radioforms.database.schema_manager import SchemaManager


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
        
        Uses the SchemaManager for robust schema versioning and migration.
        """
        try:
            # Use the enhanced schema manager for versioning and migrations
            schema_manager = SchemaManager(self._db_path)
            
            # Initialize schema manager
            schema_manager.initialize()
            
            # Upgrade to latest schema version
            if schema_manager.upgrade():
                # Get the current schema version after upgrade
                current_version = schema_manager.get_current_version()
                self._logger.info(f"Database initialized with schema version {current_version}")
                
                # Verify schema
                is_valid, issues = schema_manager.verify_schema()
                if not is_valid:
                    self._logger.warning(f"Schema validation found issues: {json.dumps(issues)}")
            else:
                self._logger.error("Failed to upgrade database schema")
                raise RuntimeError("Failed to upgrade database schema")
                
        except Exception as e:
            self._logger.error(f"Failed to initialize database: {e}")
            if self._conn:
                self._conn.rollback()
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
            
    def verify_schema(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify the database schema against the expected schema.
        
        Returns:
            Tuple of (is_valid, issues) where is_valid is True if the schema is valid,
            and issues is a dictionary containing any issues found.
        """
        schema_manager = SchemaManager(self._db_path)
        return schema_manager.verify_schema()
            
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
        schema_manager = SchemaManager(self._db_path)
        return schema_manager.get_current_version()
        
    def get_schema_history(self) -> List[Dict[str, Any]]:
        """
        Get the schema migration history.
        
        Returns:
            List of schema migrations with version, applied_at, and description
        """
        try:
            conn = self.connect()
            cursor = conn.execute(
                """
                SELECT version, applied_at, description
                FROM schema_version
                ORDER BY version
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self._logger.error(f"Failed to get schema history: {e}")
            return []


# Create a DatabaseManager class reference for backwards compatibility
# with existing code that expects it to be imported from db_manager
class DatabaseManager(DBManager):
    """
    Alias for DBManager class.
    
    This class is provided for backwards compatibility with code that
    imports DatabaseManager from radioforms.database.db_manager.
    """
    pass
