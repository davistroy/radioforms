#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form Registry SQL Query Fix Script.

This script updates the SQL queries in the form model registry to use the correct
column names that match the actual database schema. This addresses the 'no such column: id'
and 'table forms has no column named status' errors.
"""

import sys
import os
import logging
import re
from pathlib import Path

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_db_schema():
    """
    Get the actual database schema to determine the correct column names.
    
    Returns:
        Dictionary mapping tables to their column definitions
    """
    try:
        from radioforms.database.db_manager import DBManager
        
        # Create a temporary database
        import tempfile
        db_path = os.path.join(tempfile.mkdtemp(), "test.db")
        
        # Initialize database
        db_manager = DBManager(db_path)
        db_manager.init_db()
        
        # Get database connection
        conn = db_manager.connect()
        
        # Query the schema
        schema = {}
        
        # Get tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get columns for each table
        for table in tables:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            schema[table] = columns
            
        # Close and clean up
        conn.close()
        db_manager.close()
        
        return schema
    except Exception as e:
        logger.error(f"Error getting database schema: {e}")
        return {}


def update_form_registry_queries():
    """
    Update the SQL queries in the form model registry to use the correct column names.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the actual schema
        schema = get_db_schema()
        
        if not schema:
            logger.error("Could not get database schema")
            return False
            
        # Get the forms table schema
        forms_columns = schema.get('forms', [])
        if not forms_columns:
            logger.error("Could not find forms table in schema")
            return False
            
        logger.info(f"Forms table columns: {forms_columns}")
        
        # Path to the form_model_registry.py file
        registry_path = Path("radioforms/models/form_model_registry.py")
        
        # Check if file exists
        if not registry_path.exists():
            logger.error(f"Registry file not found: {registry_path}")
            return False
            
        # Read current content
        with open(registry_path, 'r') as f:
            content = f.read()
            
        # Track changes
        changes = []
        
        # Fix column name issues
        column_fixes = []
        
        # Check if 'id' is referenced but should be 'form_id'
        if 'id' not in forms_columns and 'form_id' in forms_columns:
            column_fixes.append(('SELECT id FROM', 'SELECT form_id FROM'))
            column_fixes.append(('WHERE id =', 'WHERE form_id ='))
            column_fixes.append(('ORDER BY id', 'ORDER BY form_id'))
            
        # Check if 'status' is referenced but doesn't exist
        if 'status' not in forms_columns:
            # Remove status from INSERT statements
            status_pattern = r'INSERT INTO forms \(.*?status.*?\) VALUES \(.*?\)'
            status_matches = re.findall(status_pattern, content, re.DOTALL)
            
            for match in status_matches:
                # Remove status from column list
                fixed_match = re.sub(r',\s*status', '', match)
                # Remove corresponding value
                fixed_match = re.sub(r',\s*\?', '', fixed_match, count=1)
                content = content.replace(match, fixed_match)
                changes.append(f"Removed status from INSERT statement")
                
            # Remove status from UPDATE statements
            update_pattern = r'UPDATE forms SET.*?status = \?.*?WHERE'
            update_matches = re.findall(update_pattern, content, re.DOTALL)
            
            for match in update_matches:
                # Remove status from SET clause
                fixed_match = re.sub(r',\s*status = \?', '', match)
                content = content.replace(match, fixed_match)
                changes.append(f"Removed status from UPDATE statement")
                
        # Apply general column name fixes
        for old, new in column_fixes:
            if old in content:
                content = content.replace(old, new)
                changes.append(f"Replaced '{old}' with '{new}'")
                
        # Fix the db_object creation for handling status field
        if 'status' not in forms_columns and '"status": state,' in content:
            # Find the db_object creation block
            db_object_pattern = r'db_object = \{.*?"status": state,.*?\}'
            db_object_match = re.search(db_object_pattern, content, re.DOTALL)
            
            if db_object_match:
                db_object_str = db_object_match.group(0)
                # Remove the status field
                fixed_db_object = re.sub(r',\s*"status": state,', ',', db_object_str)
                content = content.replace(db_object_str, fixed_db_object)
                changes.append("Removed status field from db_object")
                
        # If no changes made, we're done
        if not changes:
            logger.info("No changes needed to form registry queries")
            return False
            
        # Write updated content
        with open(registry_path, 'w') as f:
            f.write(content)
            
        # Report changes
        for change in changes:
            logger.info(f"Made change: {change}")
            
        return True
    except Exception as e:
        logger.error(f"Error updating form registry queries: {e}")
        return False


def main():
    """Run the script."""
    logger.info("Starting form registry query fix script")
    
    # Update form registry queries
    if update_form_registry_queries():
        logger.info("Successfully updated form registry queries")
    else:
        logger.warning("Form registry queries not updated")
        
    logger.info("Form registry query fix script completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
