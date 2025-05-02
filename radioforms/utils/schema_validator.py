#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Schema Validation Utility.

This module provides utilities to validate database schema against expected schema
definitions, helping to detect mismatches early in the development process.
"""

import logging
import sqlite3
from typing import Dict, List, Optional, Tuple, Set, Any
import json
import os

logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Database schema validator.
    
    This class provides utilities to validate the actual database schema against
    the expected schema definition, helping to detect mismatches early.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the schema validator.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_actual_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the actual database schema.
        
        Returns:
            Dictionary mapping table names to column definitions
        """
        if not self.conn:
            if not self.connect():
                return {}
        
        schema = {}
        
        try:
            # Get tables
            cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get columns for each table
            for table in tables:
                cursor = self.conn.execute(f"PRAGMA table_info({table})")
                columns = [dict(row) for row in cursor.fetchall()]
                schema[table] = columns
            
            return schema
        
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return {}
    
    def get_expected_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the expected database schema.
        
        This method should be overridden by subclasses to provide the expected
        schema definition for validation.
        
        Returns:
            Dictionary mapping table names to column definitions
        """
        expected_schema = {
            'forms': [
                {'name': 'form_id', 'type': 'TEXT', 'pk': 1, 'notnull': 1},
                {'name': 'incident_id', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'op_period_id', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'form_type', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'state', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'data', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'created_at', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'updated_at', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'created_by', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'updated_by', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'title', 'type': 'TEXT', 'pk': 0, 'notnull': 0}
            ],
            'form_versions': [
                {'name': 'version_id', 'type': 'TEXT', 'pk': 1, 'notnull': 1},
                {'name': 'form_id', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'version', 'type': 'INTEGER', 'pk': 0, 'notnull': 1},
                {'name': 'content', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'created_at', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'comment', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'user_id', 'type': 'TEXT', 'pk': 0, 'notnull': 0}
            ],
            'attachments': [
                {'name': 'attachment_id', 'type': 'TEXT', 'pk': 1, 'notnull': 1},
                {'name': 'form_id', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'filename', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'file_path', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'file_size', 'type': 'INTEGER', 'pk': 0, 'notnull': 0},
                {'name': 'mime_type', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'upload_time', 'type': 'TEXT', 'pk': 0, 'notnull': 1},
                {'name': 'uploader_id', 'type': 'TEXT', 'pk': 0, 'notnull': 0},
                {'name': 'description', 'type': 'TEXT', 'pk': 0, 'notnull': 0}
            ]
        }
        
        return expected_schema
    
    def validate_schema(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate the actual database schema against the expected schema.
        
        Returns:
            Tuple of (is_valid, issues) where is_valid is True if the schema is valid,
            and issues is a dictionary containing the validation issues found.
        """
        # Get schemas
        actual_schema = self.get_actual_schema()
        expected_schema = self.get_expected_schema()
        
        # Issues container
        issues = {
            "missing_tables": [],
            "missing_columns": {},
            "type_mismatches": {},
            "constraint_mismatches": {}
        }
        
        # Check missing tables
        for table_name in expected_schema:
            if table_name not in actual_schema:
                issues["missing_tables"].append(table_name)
        
        # Check columns in each table
        for table_name, expected_columns in expected_schema.items():
            if table_name not in actual_schema:
                continue
            
            actual_columns = actual_schema[table_name]
            actual_column_dict = {col['name']: col for col in actual_columns}
            
            # Check for missing columns
            missing_columns = []
            for expected_col in expected_columns:
                if expected_col['name'] not in actual_column_dict:
                    missing_columns.append(expected_col['name'])
            
            if missing_columns:
                issues["missing_columns"][table_name] = missing_columns
            
            # Check for type mismatches
            type_mismatches = []
            for expected_col in expected_columns:
                col_name = expected_col['name']
                if col_name in actual_column_dict:
                    actual_col = actual_column_dict[col_name]
                    if expected_col['type'] != actual_col['type']:
                        type_mismatches.append({
                            "column": col_name,
                            "expected_type": expected_col['type'],
                            "actual_type": actual_col['type']
                        })
            
            if type_mismatches:
                issues["type_mismatches"][table_name] = type_mismatches
            
            # Check for constraint mismatches (primary key, not null)
            constraint_mismatches = []
            for expected_col in expected_columns:
                col_name = expected_col['name']
                if col_name in actual_column_dict:
                    actual_col = actual_column_dict[col_name]
                    
                    # Check primary key
                    if expected_col.get('pk', 0) != actual_col.get('pk', 0):
                        constraint_mismatches.append({
                            "column": col_name,
                            "constraint": "primary_key",
                            "expected": expected_col.get('pk', 0),
                            "actual": actual_col.get('pk', 0)
                        })
                    
                    # Check not null
                    if expected_col.get('notnull', 0) != actual_col.get('notnull', 0):
                        constraint_mismatches.append({
                            "column": col_name,
                            "constraint": "not_null",
                            "expected": expected_col.get('notnull', 0),
                            "actual": actual_col.get('notnull', 0)
                        })
            
            if constraint_mismatches:
                issues["constraint_mismatches"][table_name] = constraint_mismatches
        
        # Check if there are any issues
        is_valid = (
            not issues["missing_tables"] and
            not issues["missing_columns"] and
            not issues["type_mismatches"] and
            not issues["constraint_mismatches"]
        )
        
        return is_valid, issues
    
    def format_validation_issues(self, issues: Dict[str, Any]) -> str:
        """
        Format validation issues into a human-readable string.
        
        Args:
            issues: Dictionary containing the validation issues
            
        Returns:
            Human-readable string describing the issues
        """
        lines = ["Database Schema Validation Issues:"]
        
        # Missing tables
        if issues["missing_tables"]:
            lines.append("\nMissing Tables:")
            for table_name in issues["missing_tables"]:
                lines.append(f"  - {table_name}")
        
        # Missing columns
        if issues["missing_columns"]:
            lines.append("\nMissing Columns:")
            for table_name, columns in issues["missing_columns"].items():
                lines.append(f"  Table: {table_name}")
                for column in columns:
                    lines.append(f"    - {column}")
        
        # Type mismatches
        if issues["type_mismatches"]:
            lines.append("\nColumn Type Mismatches:")
            for table_name, mismatches in issues["type_mismatches"].items():
                lines.append(f"  Table: {table_name}")
                for mismatch in mismatches:
                    lines.append(f"    - {mismatch['column']}: Expected {mismatch['expected_type']}, got {mismatch['actual_type']}")
        
        # Constraint mismatches
        if issues["constraint_mismatches"]:
            lines.append("\nConstraint Mismatches:")
            for table_name, mismatches in issues["constraint_mismatches"].items():
                lines.append(f"  Table: {table_name}")
                for mismatch in mismatches:
                    lines.append(f"    - {mismatch['column']}: {mismatch['constraint']} - Expected {mismatch['expected']}, got {mismatch['actual']}")
        
        return "\n".join(lines)
    
    def generate_migration_sql(self, issues: Dict[str, Any]) -> List[str]:
        """
        Generate SQL statements to fix the schema issues.
        
        Args:
            issues: Dictionary containing the validation issues
            
        Returns:
            List of SQL statements to fix the issues
        """
        expected_schema = self.get_expected_schema()
        sql_statements = []
        
        # Create missing tables
        for table_name in issues["missing_tables"]:
            columns = expected_schema[table_name]
            column_defs = []
            
            for col in columns:
                # Build the column definition
                col_def = f"{col['name']} {col['type']}"
                
                if col.get('pk', 0) == 1:
                    col_def += " PRIMARY KEY"
                
                if col.get('notnull', 0) == 1:
                    col_def += " NOT NULL"
                
                if col.get('dflt_value') is not None:
                    col_def += f" DEFAULT {col['dflt_value']}"
                
                column_defs.append(col_def)
            
            # Create the table
            create_stmt = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(column_defs) + "\n);"
            sql_statements.append(create_stmt)
        
        # Add missing columns
        for table_name, columns in issues["missing_columns"].items():
            for column_name in columns:
                # Find the column definition in the expected schema
                column_def = next((col for col in expected_schema[table_name] if col['name'] == column_name), None)
                
                if column_def:
                    # Build the column definition
                    col_def = f"{column_name} {column_def['type']}"
                    
                    if column_def.get('notnull', 0) == 1:
                        col_def += " NOT NULL"
                    
                    if column_def.get('dflt_value') is not None:
                        col_def += f" DEFAULT {column_def['dflt_value']}"
                    
                    # Add the column
                    alter_stmt = f"ALTER TABLE {table_name} ADD COLUMN {col_def};"
                    sql_statements.append(alter_stmt)
        
        return sql_statements
    
    def save_validation_report(self, issues: Dict[str, Any], report_path: str) -> bool:
        """
        Save the validation issues to a report file.
        
        Args:
            issues: Dictionary containing the validation issues
            report_path: Path to save the report to
            
        Returns:
            True if the report was saved successfully, False otherwise
        """
        try:
            # Create report directory if it doesn't exist
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            # Format the report
            report = self.format_validation_issues(issues)
            
            # Add migration SQL
            sql_statements = self.generate_migration_sql(issues)
            if sql_statements:
                report += "\n\nMigration SQL:\n\n"
                for stmt in sql_statements:
                    report += f"{stmt}\n"
            
            # Save to file
            with open(report_path, 'w') as f:
                f.write(report)
            
            logger.info(f"Validation report saved to {report_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")
            return False


def validate_database(db_path: str, report_path: Optional[str] = None) -> bool:
    """
    Validate a database schema and optionally save a report.
    
    Args:
        db_path: Path to the database file
        report_path: Optional path to save the validation report to
        
    Returns:
        True if the schema is valid, False otherwise
    """
    validator = SchemaValidator(db_path)
    is_valid, issues = validator.validate_schema()
    
    if not is_valid and report_path:
        validator.save_validation_report(issues, report_path)
    
    validator.close()
    return is_valid


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: schema_validator.py <database_path> [report_path]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    report_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if validate_database(db_path, report_path):
        print("Schema validation passed!")
        sys.exit(0)
    else:
        print(f"Schema validation failed! Report saved to {report_path}")
        sys.exit(1)
