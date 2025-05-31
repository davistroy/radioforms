"""Form service for database CRUD operations.

This module provides the service layer between the UI and database,
handling all form persistence operations following CLAUDE.md principles.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from ..database.connection import DatabaseManager, DatabaseError
from ..forms.ics213 import ICS213Form, ICS213Data, FormStatus


logger = logging.getLogger(__name__)


class FormService:
    """Service for managing form persistence operations.
    
    This class provides a clean interface between the UI and database,
    handling all CRUD operations for ICS-213 forms.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize form service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        self.logger.debug("FormService initialized")
    
    def save_form(self, form: ICS213Form, form_id: Optional[int] = None) -> int:
        """Save form to database.
        
        Args:
            form: ICS213Form to save
            form_id: Existing form ID for updates, None for new forms
            
        Returns:
            Form ID of saved form
            
        Raises:
            DatabaseError: If save operation fails
        """
        try:
            # Serialize form data
            form_data_json = form.to_json()
            
            # Generate form metadata
            form_number = self._generate_form_number(form)
            incident_name = form.data.incident_name or "Untitled Incident"
            title = form.data.subject or "Untitled Message"
            created_by = form.data.from_person.display_name or "Unknown"
            
            with self.db_manager.get_transaction() as conn:
                if form_id is None:
                    # Insert new form
                    cursor = conn.execute(
                        """
                        INSERT INTO forms 
                        (form_type, form_number, incident_name, title, data, 
                         created_by, status, version)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            "ICS-213",
                            form_number,
                            incident_name,
                            title,
                            form_data_json,
                            created_by,
                            form.status.value,
                            1
                        )
                    )
                    form_id = cursor.lastrowid
                    self.logger.info(f"Created new form with ID {form_id}")
                    
                else:
                    # Update existing form
                    conn.execute(
                        """
                        UPDATE forms 
                        SET form_number = ?, incident_name = ?, title = ?, data = ?,
                            status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            form_number,
                            incident_name,
                            title,
                            form_data_json,
                            form.status.value,
                            form_id
                        )
                    )
                    self.logger.info(f"Updated form with ID {form_id}")
                
                # Create version entry
                self._create_form_version(conn, form_id, form_data_json, created_by)
            
            return form_id
            
        except Exception as e:
            error_msg = f"Failed to save form: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def load_form(self, form_id: int) -> ICS213Form:
        """Load form from database.
        
        Args:
            form_id: ID of form to load
            
        Returns:
            Loaded ICS213Form
            
        Raises:
            DatabaseError: If form not found or load fails
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT data, status, created_at, updated_at
                    FROM forms 
                    WHERE id = ? AND form_type = 'ICS-213'
                    """,
                    (form_id,)
                )
                
                result = cursor.fetchone()
                if not result:
                    raise DatabaseError(f"Form with ID {form_id} not found")
                
                data_json, status_value, created_at, updated_at = result
                
                # Deserialize form
                form = ICS213Form.from_json(data_json)
                
                # Set metadata
                try:
                    form.status = FormStatus(status_value)
                except ValueError:
                    form.status = FormStatus.DRAFT
                
                # Parse timestamps if available
                if created_at:
                    try:
                        form.created_at = datetime.fromisoformat(created_at)
                    except ValueError:
                        pass
                
                if updated_at:
                    try:
                        form.updated_at = datetime.fromisoformat(updated_at)
                    except ValueError:
                        pass
                
                self.logger.info(f"Loaded form with ID {form_id}")
                return form
                
        except DatabaseError:
            raise
        except Exception as e:
            error_msg = f"Failed to load form {form_id}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def list_forms(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List forms in database.
        
        Args:
            limit: Maximum number of forms to return
            offset: Number of forms to skip
            
        Returns:
            List of form summaries
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT id, form_number, incident_name, title, status, 
                           created_by, created_at, updated_at
                    FROM forms 
                    WHERE form_type = 'ICS-213'
                    ORDER BY updated_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset)
                )
                
                forms = []
                for row in cursor.fetchall():
                    forms.append({
                        'id': row[0],
                        'form_number': row[1],
                        'incident_name': row[2],
                        'title': row[3],
                        'status': row[4],
                        'created_by': row[5],
                        'created_at': row[6],
                        'updated_at': row[7]
                    })
                
                self.logger.debug(f"Listed {len(forms)} forms")
                return forms
                
        except Exception as e:
            error_msg = f"Failed to list forms: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def delete_form(self, form_id: int) -> bool:
        """Delete form from database.
        
        Args:
            form_id: ID of form to delete
            
        Returns:
            True if form was deleted
            
        Raises:
            DatabaseError: If delete operation fails
        """
        try:
            with self.db_manager.get_transaction() as conn:
                cursor = conn.execute(
                    "DELETE FROM forms WHERE id = ? AND form_type = 'ICS-213'",
                    (form_id,)
                )
                
                if cursor.rowcount == 0:
                    self.logger.warning(f"No form found with ID {form_id}")
                    return False
                
                self.logger.info(f"Deleted form with ID {form_id}")
                return True
                
        except Exception as e:
            error_msg = f"Failed to delete form {form_id}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def search_forms(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search forms by text content.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching form summaries
        """
        try:
            with self.db_manager.get_connection() as conn:
                # Simple text search in title, incident_name, and created_by
                search_pattern = f"%{query}%"
                cursor = conn.execute(
                    """
                    SELECT id, form_number, incident_name, title, status, 
                           created_by, created_at, updated_at
                    FROM forms 
                    WHERE form_type = 'ICS-213' AND (
                        title LIKE ? OR 
                        incident_name LIKE ? OR 
                        created_by LIKE ? OR
                        form_number LIKE ?
                    )
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (search_pattern, search_pattern, search_pattern, search_pattern, limit)
                )
                
                forms = []
                for row in cursor.fetchall():
                    forms.append({
                        'id': row[0],
                        'form_number': row[1],
                        'incident_name': row[2],
                        'title': row[3],
                        'status': row[4],
                        'created_by': row[5],
                        'created_at': row[6],
                        'updated_at': row[7]
                    })
                
                self.logger.debug(f"Search '{query}' returned {len(forms)} forms")
                return forms
                
        except Exception as e:
            error_msg = f"Failed to search forms: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def get_form_count(self) -> int:
        """Get total number of forms in database.
        
        Returns:
            Total form count
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM forms WHERE form_type = 'ICS-213'"
                )
                
                count = cursor.fetchone()[0]
                self.logger.debug(f"Total forms: {count}")
                return count
                
        except Exception as e:
            error_msg = f"Failed to get form count: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def _generate_form_number(self, form: ICS213Form) -> str:
        """Generate unique form number.
        
        Args:
            form: Form to generate number for
            
        Returns:
            Generated form number
        """
        # Simple format: ICS213-YYYYMMDD-HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"ICS213-{timestamp}"
    
    def _create_form_version(self, conn, form_id: int, data_json: str, changed_by: str):
        """Create form version entry.
        
        Args:
            conn: Database connection
            form_id: Form ID
            data_json: Form data as JSON
            changed_by: Who made the change
        """
        try:
            # Get current version number
            cursor = conn.execute(
                "SELECT MAX(version) FROM form_versions WHERE form_id = ?",
                (form_id,)
            )
            result = cursor.fetchone()
            version = (result[0] or 0) + 1
            
            # Insert version record
            conn.execute(
                """
                INSERT INTO form_versions 
                (form_id, version, data, changed_by, change_description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    form_id,
                    version,
                    data_json,
                    changed_by,
                    f"Form saved - version {version}"
                )
            )
            
            self.logger.debug(f"Created version {version} for form {form_id}")
            
        except Exception as e:
            # Don't fail the main operation for version tracking
            self.logger.warning(f"Failed to create form version: {e}")
    
    def validate_form_data(self, form: ICS213Form) -> List[str]:
        """Validate form before saving.
        
        Args:
            form: Form to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Basic form validation
        if not form.validate():
            errors.extend(form.get_validation_errors())
        
        # Additional business rules
        if form.data.incident_name and len(form.data.incident_name) > 100:
            errors.append("Incident name too long (max 100 characters)")
        
        if form.data.subject and len(form.data.subject) > 200:
            errors.append("Subject too long (max 200 characters)")
        
        if form.data.message and len(form.data.message) > 5000:
            errors.append("Message too long (max 5000 characters)")
        
        return errors