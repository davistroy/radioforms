#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database management module for SQLite operations.
"""

import os
import sqlite3
import threading
from pathlib import Path


class DatabaseManager:
    """
    Manages SQLite database connections and operations with support for
    WAL mode and thread safety.
    """
    
    def __init__(self, db_path, wal_mode=True):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
            wal_mode: Whether to use Write-Ahead Logging mode for better concurrency
        """
        self.db_path = Path(db_path)
        self.wal_mode = wal_mode
        self.connection = None
        
        # Create a thread-local storage for database connections
        self._local = threading.local()
        
        # Ensure the database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directory if there is a directory path
            os.makedirs(db_dir, exist_ok=True)
        
        # Initialize the database
        self._init_db()
        
    def _init_db(self):
        """Initialize the database, creating it if it doesn't exist."""
        conn = self._get_connection()
        
        # Set pragmas for performance and data integrity
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency if specified
        if self.wal_mode:
            cursor.execute("PRAGMA journal_mode=WAL;")
            
        # Other recommended SQLite settings
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA temp_store=MEMORY;")
        
        # Create tables if they don't exist
        self._create_tables(cursor)
        
        conn.commit()
        
    def _create_tables(self, cursor):
        """
        Create database tables if they don't exist.
        
        Args:
            cursor: SQLite cursor object
        """
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            call_sign TEXT,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create incidents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create forms table to store form metadata
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            form_type TEXT NOT NULL,
            title TEXT NOT NULL,
            creator_id INTEGER,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(id),
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
        ''')
        
        # Create form_versions table for version history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES forms(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        ''')
        
        # Create attachments table for form attachments
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
        
        # Create settings table for application settings
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
    def _get_connection(self):
        """
        Get a database connection for the current thread.
        
        Returns:
            A SQLite connection object for the current thread
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            
            # Enable foreign key support for each connection
            self._local.connection.execute("PRAGMA foreign_keys=ON;")
            
            # Configure connection to return rows as dictionaries
            self._local.connection.row_factory = sqlite3.Row
            
        return self._local.connection
        
    def execute(self, query, params=None):
        """
        Execute a SQL query with optional parameters.
        
        Args:
            query: SQL query string
            params: Parameters for the query
            
        Returns:
            Cursor object with query results
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        return cursor
        
    def execute_many(self, query, params_list):
        """
        Execute a SQL query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter sets
            
        Returns:
            Cursor object
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        return cursor
        
    def commit(self):
        """Commit the current transaction."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.commit()
            
    def rollback(self):
        """Roll back the current transaction."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.rollback()
            
    def close(self):
        """Close the database connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            
    def transaction(self):
        """
        Create a context manager for a database transaction.
        
        Returns:
            A transaction context manager
        """
        return DatabaseTransaction(self)
            
            
class DatabaseTransaction:
    """Context manager for database transactions."""
    
    def __init__(self, db_manager):
        """
        Initialize a database transaction.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        
    def __enter__(self):
        """Enter the transaction context."""
        return self.db_manager
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the transaction context.
        
        Commits the transaction if no exception occurred, otherwise
        rolls back the transaction.
        """
        if exc_type is None:
            self.db_manager.commit()
        else:
            self.db_manager.rollback()
            
        return False  # Re-raise any exceptions
