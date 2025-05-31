"""Database schema definition and management.

This module defines the database schema for RadioForms and provides
utilities for schema creation, validation, and migration.
"""

import logging
from typing import Dict, List, Any
from pathlib import Path

from .connection import DatabaseManager, DatabaseError


# Schema version for migration tracking
SCHEMA_VERSION = 1

# SQL statements for table creation
CREATE_TABLES_SQL = """
-- RadioForms Database Schema v1.0
-- Simple schema for Phase 1 MVP (ICS-213 focus)

-- Application metadata table
CREATE TABLE IF NOT EXISTS app_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forms table - stores all form data as JSON
CREATE TABLE IF NOT EXISTS forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_type TEXT NOT NULL,  -- 'ICS-213', 'ICS-214', etc.
    form_number TEXT,         -- User-assigned form number/identifier
    incident_name TEXT,       -- Incident this form belongs to
    title TEXT,              -- Form title/subject
    data TEXT NOT NULL,      -- JSON data for the form
    created_by TEXT,         -- Who created this form
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    status TEXT DEFAULT 'draft'  -- 'draft', 'submitted', 'approved'
);

-- Form versions table - tracks form history
CREATE TABLE IF NOT EXISTS form_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    data TEXT NOT NULL,      -- JSON snapshot of form at this version
    changed_by TEXT,         -- Who made this change
    change_description TEXT, -- What was changed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE CASCADE,
    UNIQUE(form_id, version)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_forms_type ON forms(form_type);
CREATE INDEX IF NOT EXISTS idx_forms_incident ON forms(incident_name);
CREATE INDEX IF NOT EXISTS idx_forms_created_at ON forms(created_at);
CREATE INDEX IF NOT EXISTS idx_forms_updated_at ON forms(updated_at);
CREATE INDEX IF NOT EXISTS idx_forms_created_by ON forms(created_by);
CREATE INDEX IF NOT EXISTS idx_forms_status ON forms(status);
CREATE INDEX IF NOT EXISTS idx_form_versions_form_id ON form_versions(form_id);

-- Create triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_forms_timestamp 
    AFTER UPDATE ON forms
    FOR EACH ROW
    BEGIN
        UPDATE forms SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_metadata_timestamp 
    AFTER UPDATE ON app_metadata
    FOR EACH ROW
    BEGIN
        UPDATE app_metadata SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
    END;
"""

# Default metadata values
DEFAULT_METADATA = {
    'schema_version': str(SCHEMA_VERSION),
    'app_version': '0.1.0',
    'created_at': 'CURRENT_TIMESTAMP',
    'database_type': 'radioforms_primary'
}


class SchemaManager:
    """Manages database schema creation, validation, and migration.
    
    This class handles:
    - Initial database schema creation
    - Schema version tracking
    - Basic migration support
    - Schema validation
    
    Example:
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
    """
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize schema manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def initialize_database(self) -> None:
        """Initialize database with schema and default data.
        
        This method:
        1. Creates all tables if they don't exist
        2. Sets up indexes and triggers
        3. Inserts default metadata
        4. Validates the schema
        
        Raises:
            DatabaseError: If initialization fails
        """
        self.logger.info("Initializing database schema...")
        
        try:
            # Create tables and indexes
            self.db_manager.execute_script(CREATE_TABLES_SQL)
            
            # Insert default metadata
            self._insert_default_metadata()
            
            # Validate schema
            self.validate_schema()
            
            self.logger.info("Database schema initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize database schema: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def _insert_default_metadata(self) -> None:
        """Insert default metadata values."""
        try:
            with self.db_manager.get_transaction() as conn:
                for key, value in DEFAULT_METADATA.items():
                    # Use INSERT OR IGNORE to avoid duplicates
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO app_metadata (key, value) 
                        VALUES (?, ?)
                        """,
                        (key, value)
                    )
            
            self.logger.debug("Default metadata inserted")
            
        except Exception as e:
            raise DatabaseError(f"Failed to insert default metadata: {e}") from e
    
    def validate_schema(self) -> bool:
        """Validate database schema integrity.
        
        Returns:
            True if schema is valid
            
        Raises:
            DatabaseError: If schema validation fails
        """
        self.logger.debug("Validating database schema...")
        
        try:
            with self.db_manager.get_connection() as conn:
                # Check that required tables exist
                required_tables = ['app_metadata', 'forms', 'form_versions']
                
                cursor = conn.execute(
                    """
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ({})
                    """.format(','.join('?' * len(required_tables))),
                    required_tables
                )
                
                existing_tables = set(row[0] for row in cursor.fetchall())
                missing_tables = set(required_tables) - existing_tables
                
                if missing_tables:
                    raise DatabaseError(f"Missing required tables: {missing_tables}")
                
                # Check schema version
                cursor = conn.execute(
                    "SELECT value FROM app_metadata WHERE key = 'schema_version'"
                )
                result = cursor.fetchone()
                
                if not result:
                    raise DatabaseError("Schema version not found in metadata")
                
                schema_version = int(result[0])
                if schema_version != SCHEMA_VERSION:
                    self.logger.warning(
                        f"Schema version mismatch: expected {SCHEMA_VERSION}, got {schema_version}"
                    )
                
                # Validate foreign key constraints
                cursor = conn.execute("PRAGMA foreign_key_check")
                fk_errors = cursor.fetchall()
                
                if fk_errors:
                    raise DatabaseError(f"Foreign key constraint violations: {fk_errors}")
                
                self.logger.debug("Schema validation completed successfully")
                return True
                
        except Exception as e:
            error_msg = f"Schema validation failed: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the current schema.
        
        Returns:
            Dictionary with schema information
        """
        try:
            with self.db_manager.get_connection() as conn:
                info = {}
                
                # Get schema version
                cursor = conn.execute(
                    "SELECT value FROM app_metadata WHERE key = 'schema_version'"
                )
                result = cursor.fetchone()
                info['schema_version'] = int(result[0]) if result else None
                
                # Get table information
                cursor = conn.execute(
                    """
                    SELECT name, sql FROM sqlite_master 
                    WHERE type='table' 
                    ORDER BY name
                    """
                )
                
                tables = {}
                for row in cursor.fetchall():
                    table_name = row[0]
                    
                    # Get column information
                    col_cursor = conn.execute(f"PRAGMA table_info({table_name})")
                    columns = [
                        {
                            'name': col[1],
                            'type': col[2],
                            'not_null': bool(col[3]),
                            'default': col[4],
                            'primary_key': bool(col[5])
                        }
                        for col in col_cursor.fetchall()
                    ]
                    
                    # Get row count
                    count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = count_cursor.fetchone()[0]
                    
                    tables[table_name] = {
                        'columns': columns,
                        'row_count': row_count,
                        'sql': row[1]
                    }
                
                info['tables'] = tables
                
                # Get index information
                cursor = conn.execute(
                    """
                    SELECT name, tbl_name FROM sqlite_master 
                    WHERE type='index' AND sql IS NOT NULL
                    ORDER BY name
                    """
                )
                
                indexes = [
                    {'name': row[0], 'table': row[1]}
                    for row in cursor.fetchall()
                ]
                
                info['indexes'] = indexes
                
                return info
                
        except Exception as e:
            self.logger.error(f"Failed to get schema info: {e}")
            return {'error': str(e)}
    
    def reset_database(self) -> None:
        """Reset database by dropping all tables and recreating schema.
        
        WARNING: This will delete all data!
        
        Raises:
            DatabaseError: If reset fails
        """
        self.logger.warning("Resetting database - ALL DATA WILL BE LOST!")
        
        try:
            with self.db_manager.get_transaction() as conn:
                # Drop all tables
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    if table != 'sqlite_sequence':  # Don't drop SQLite internal table
                        conn.execute(f"DROP TABLE IF EXISTS {table}")
                        self.logger.debug(f"Dropped table: {table}")
            
            # Recreate schema
            self.initialize_database()
            
            self.logger.info("Database reset completed successfully")
            
        except Exception as e:
            error_msg = f"Failed to reset database: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def create_sample_data(self) -> None:
        """Create sample data for testing and development.
        
        This method inserts sample forms for development and testing purposes.
        """
        self.logger.info("Creating sample data...")
        
        sample_forms = [
            {
                'form_type': 'ICS-213',
                'form_number': 'MSG-001',
                'incident_name': 'Sample Training Incident',
                'title': 'Initial Status Report',
                'data': '''{
                    "to": "Incident Commander",
                    "from": "Operations Section Chief",
                    "subject": "Initial Status Report",
                    "date": "2025-05-30",
                    "time": "14:30",
                    "message": "All units are in position and ready to begin operations. Weather conditions are favorable. No safety concerns at this time.",
                    "reply_requested": false,
                    "priority": "routine"
                }''',
                'created_by': 'Training User',
                'status': 'draft'
            },
            {
                'form_type': 'ICS-213',
                'form_number': 'MSG-002',
                'incident_name': 'Sample Training Incident',
                'title': 'Resource Request',
                'data': '''{
                    "to": "Logistics Section Chief",
                    "from": "Division A Supervisor",
                    "subject": "Additional Resources Needed",
                    "date": "2025-05-30",
                    "time": "15:45",
                    "message": "Request 2 additional engine companies for structure protection. ETA needed ASAP.",
                    "reply_requested": true,
                    "priority": "urgent"
                }''',
                'created_by': 'Training User',
                'status': 'submitted'
            }
        ]
        
        try:
            with self.db_manager.get_transaction() as conn:
                for form_data in sample_forms:
                    conn.execute(
                        """
                        INSERT INTO forms 
                        (form_type, form_number, incident_name, title, data, created_by, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            form_data['form_type'],
                            form_data['form_number'],
                            form_data['incident_name'],
                            form_data['title'],
                            form_data['data'],
                            form_data['created_by'],
                            form_data['status']
                        )
                    )
            
            self.logger.info(f"Created {len(sample_forms)} sample forms")
            
        except Exception as e:
            error_msg = f"Failed to create sample data: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e