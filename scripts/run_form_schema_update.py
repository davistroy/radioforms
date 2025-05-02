#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run the form schema update migration.

This script runs the form_schema_update migration to fix any schema discrepancies
in the forms table that may be causing integration issues between the form models
and the database layer.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path to import radioforms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from radioforms.database.db_manager import DBManager
from radioforms.database.migrations.form_schema_update import run_migration


def setup_logging():
    """
    Set up logging configuration.
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger('form_schema_update')
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def main():
    """
    Main function to run the migration.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run form schema update migration')
    parser.add_argument('--db-path', type=str, help='Path to the database file')
    parser.add_argument('--force', action='store_true', help='Force migration regardless of schema version')
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging()
    
    # Determine database path
    db_path = args.db_path
    if not db_path:
        # Get from environment or use default
        db_path = os.environ.get('RADIOFORMS_DB_PATH')
        
        if not db_path:
            # Try to determine from config directory
            config_dir = os.environ.get('RADIOFORMS_CONFIG_DIR')
            if not config_dir:
                config_dir = os.path.join(os.path.expanduser('~'), '.radioforms')
            
            db_path = os.path.join(config_dir, 'radioforms.db')
    
    logger.info(f"Using database at: {db_path}")
    
    # Create DB manager to check schema version if not forcing
    if not args.force:
        try:
            db_manager = DBManager(db_path)
            schema_version = db_manager.get_schema_version()
            
            if schema_version >= 3:
                logger.info(f"Schema version is already {schema_version}, no need to run migration")
                return 0
                
            logger.info(f"Current schema version: {schema_version}, will update to version 3")
        except Exception as e:
            logger.error(f"Error checking schema version: {e}")
            return 1
    
    # Run migration
    try:
        logger.info("Running form schema update migration...")
        success, message = run_migration(db_path)
        
        if success:
            logger.info(f"Migration successful: {message}")
            
            # Update schema version if needed
            if not args.force:
                try:
                    db_manager = DBManager(db_path)
                    conn = db_manager.connect()
                    
                    # Ensure schema_version table exists
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS schema_version (
                            version INTEGER PRIMARY KEY,
                            applied_at TIMESTAMP NOT NULL,
                            description TEXT
                        )
                    """)
                    
                    if db_manager.get_schema_version() < 3:
                        conn.execute(
                            "INSERT INTO schema_version (version, applied_at, description) VALUES (?, datetime('now'), ?)",
                            (3, "Updated forms table schema to fix discrepancies")
                        )
                        db_manager.commit()
                        logger.info("Updated schema version to 3")
                except Exception as e:
                    logger.error(f"Error updating schema version: {e}")
                    return 1
            
            return 0
        else:
            logger.error(f"Migration failed: {message}")
            return 1
    except Exception as e:
        logger.error(f"Error running migration: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
