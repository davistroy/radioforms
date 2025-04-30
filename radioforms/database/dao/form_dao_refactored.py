#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form Data Access Object (DAO) for database operations related to forms.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import json
from datetime import datetime

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.models.form import Form, FormStatus
from radioforms.database.models.form_version import FormVersion
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.dao_cache_mixin import DAOCacheMixin


class FormDAO(DAOCacheMixin[Form], BaseDAO[Form]):
    """
    Data Access Object for Form entities, providing database operations
    for creating, retrieving, updating, and deleting forms, including
    versioning and content management.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the FormDAO with a database manager.
        
        Args:
            db_manager: Database manager for database operations
        """
        BaseDAO.__init__(self, db_manager)
        DAOCacheMixin.__init__(self)
        self.table_name = "forms"
        self.pk_column = "id"
        
    def _row_to_entity(self, row: Dict[str, Any]) -> Form:
        """
        Convert a database row to a Form entity.
        
        Args:
            row: Dictionary containing column names and values
            
        Returns:
            A Form entity
        """
        return Form(
            id=row.get('id'),
            incident_id=row.get('incident_id'),
            form_type=row.get('form_type', ''),
            title=row.get('title', ''),
            creator_id=row.get('creator_id'),
            status=row.get('status'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
        
    def _entity_to_values(self, entity: Form) -> Dict[str, Any]:
        """
        Convert a Form entity to a dictionary of column values.
        
        Args:
            entity: The Form entity
            
        Returns:
            Dictionary containing column names and values
        """
        values = {
            'incident_id': entity.incident_id,
            'form_type': entity.form_type,
            'title': entity.title,
            'creator_id': entity.creator_id,
            'status': str(entity.status),
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values
        
    def create_with_content(self, form: Union[Form, Dict[str, Any]], content: Union[str, Dict[str, Any]], 
                           user_id: Optional[int] = None) -> int:
        """
        Create a new form with its initial content version.
        
        Args:
            form: The form entity or dictionary to create
            content: The form content as JSON string or dictionary
            user_id: ID of the user creating the form (optional)
            
        Returns:
            The ID of the created form
            
        Examples:
            >>> form = Form(form_type="ICS-213", title="Message Form")
            >>> content = {"to": "Operations", "from": "Planning", "message": "Test"}
            >>> form_id = form_dao.create_with_content(form, content, user_id=1)
        """
        with self.db_manager.transaction() as tx:
            # Handle form data based on its type
            if isinstance(form, Form):
                # Extract values from Form object
                incident_id = form.incident_id
                form_type = form.form_type
                title = form.title
                creator_id = form.creator_id or user_id
                status = str(form.status)
                created_at = form.created_at or datetime.now()
                updated_at = form.updated_at or datetime.now()
            else:
                # Extract values from dictionary
                incident_id = form.get('incident_id')
                form_type = form.get('form_type', '')
                title = form.get('title', '')
                creator_id = form.get('creator_id') or user_id
                status = form.get('status', FormStatus.DRAFT)
                status = status if isinstance(status, str) else str(status)
                created_at = form.get('created_at') or datetime.now()
                updated_at = form.get('updated_at') or datetime.now()
            
            # Create the form first
            cursor = tx.execute(
                f"""
                INSERT INTO {self.table_name} (
                    incident_id, form_type, title, creator_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id, form_type, title, 
                    creator_id, status, created_at, updated_at
                )
            )
            
            # Get the form ID
            form_id = cursor.lastrowid
            
            # Create the initial version
            content_str = content if isinstance(content, str) else json.dumps(content)
            
            # Get creator ID based on form type
            creator_for_version = user_id
            if isinstance(form, Form):
                creator_for_version = user_id or form.creator_id
            else:
                creator_for_version = user_id or form.get('creator_id')
                
            tx.execute(
                """
                INSERT INTO form_versions (
                    form_id, version_number, content, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (form_id, 1, content_str, creator_for_version, datetime.now())
            )
            
            return form_id
            
    def update_with_content(self, form: Form, content: Union[str, Dict[str, Any]], 
                           user_id: Optional[int] = None) -> bool:
        """
        Update a form and create a new content version.
        
        Args:
            form: The form entity to update
            content: The new form content as JSON string or dictionary
            user_id: ID of the user updating the form (optional)
            
        Returns:
            True if the form was updated, False otherwise
            
        Examples:
            >>> form = form_dao.find_by_id(5)
            >>> content = {"to": "Logistics", "from": "Operations", "message": "Updated"}
            >>> success = form_dao.update_with_content(form, content, user_id=2)
        """
        with self.db_manager.transaction() as tx:
            # Update the form first
            cursor = tx.execute(
                f"""
                UPDATE {self.table_name} SET
                    incident_id = ?,
                    form_type = ?,
                    title = ?,
                    status = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    form.incident_id, form.form_type, form.title, 
                    str(form.status), datetime.now(), form.id
                )
            )
            
            # Check if form was updated
            if cursor.rowcount == 0:
                return False
                
            # Get the latest version number
            cursor = tx.execute(
                "SELECT MAX(version_number) FROM form_versions WHERE form_id = ?",
                (form.id,)
            )
            result = cursor.fetchone()
            latest_version = result[0] if result and result[0] else 0
            
            # Create a new version
            content_str = content if isinstance(content, str) else json.dumps(content)
            tx.execute(
                """
                INSERT INTO form_versions (
                    form_id, version_number, content, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (form.id, latest_version + 1, content_str, user_id or form.creator_id, datetime.now())
            )
            
            return True
            
    def find_with_content(self, form_id: int, version: Optional[int] = None, 
                         as_dict: bool = False) -> Optional[Union[
                             Tuple[Form, Dict[str, Any]], 
                             Tuple[Dict[str, Any], Dict[str, Any]]
                         ]]:
        """
        Find a form with its content, optionally at a specific version.
        
        Args:
            form_id: ID of the form to get
            version: Version number to retrieve (default: latest)
            as_dict: When True, return form as dictionary instead of entity object
            
        Returns:
            Tuple of (form, content dictionary) if found, None otherwise.
            Form will be entity or dictionary based on as_dict parameter.
            
        Examples:
            >>> form_data = form_dao.find_with_content(5)
            >>> if form_data:
            >>>     form, content = form_data
            >>>     print(f"Form {form.title} content: {content}")
            >>>
            >>> # Get specific version as dict
            >>> form_data = form_dao.find_with_content(5, version=3, as_dict=True)
        """
        # Get the form first
        form = self.find_by_id(form_id, as_dict=as_dict)
        if not form:
            return None
            
        # Build the query for the version
        if version is not None:
            query = """
                SELECT * FROM form_versions
                WHERE form_id = ? AND version_number = ?
            """
            params = (form_id, version)
        else:
            query = """
                SELECT * FROM form_versions
                WHERE form_id = ?
                ORDER BY version_number DESC
                LIMIT 1
            """
            params = (form_id,)
            
        # Get the version
        cursor = self.db_manager.execute(query, params)
        version_row = cursor.fetchone()
        
        if not version_row:
            return None
            
        # Convert to objects
        content_str = version_row['content']
        
        try:
            content_dict = json.loads(content_str) if content_str else {}
        except json.JSONDecodeError:
            content_dict = {}
            
        return (form, content_dict)
        
    def find_versions(self, form_id: int) -> List[FormVersion]:
        """
        Find all versions of a form.
        
        Args:
            form_id: ID of the form
            
        Returns:
            List of FormVersion entities
            
        Examples:
            >>> versions = form_dao.find_versions(5)
            >>> for version in versions:
            >>>     print(f"Version {version.version_number} created at {version.created_at}")
        """
        query = """
            SELECT * FROM form_versions
            WHERE form_id = ?
            ORDER BY version_number
        """
        
        cursor = self.db_manager.execute(query, (form_id,))
        versions = []
        
        for row in cursor.fetchall():
            version = FormVersion(
                id=row['id'],
                form_id=row['form_id'],
                version_number=row['version_number'],
                content=row['content'],
                created_by=row['created_by'],
                created_at=row['created_at']
            )
            versions.append(version)
            
        return versions
        
    def find_by_incident(self, incident_id: int, 
                        as_dict: bool = False,
                        status: Optional[Union[FormStatus, str]] = None) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Find forms belonging to an incident, optionally filtered by status.
        
        Args:
            incident_id: ID of the incident
            as_dict: When True, return dictionaries instead of entity objects
            status: Optional status to filter by
            
        Returns:
            List of matching forms as either entity objects or dictionaries
            
        Examples:
            >>> incident_forms = form_dao.find_by_incident(3)
            >>> draft_forms = form_dao.find_by_incident(3, status=FormStatus.DRAFT)
            >>> form_dicts = form_dao.find_by_incident(3, as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name} WHERE incident_id = ?"
        params = [incident_id]
        
        # Add status filter if provided
        if status is not None:
            status_str = status if isinstance(status, str) else str(status)
            query += " AND status = ?"
            params.append(status_str)
            
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
        
    def find_by_user(self, user_id: int, 
                    as_dict: bool = False,
                    status: Optional[Union[FormStatus, str]] = None) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Find forms created by a user, optionally filtered by status.
        
        Args:
            user_id: ID of the creator
            as_dict: When True, return dictionaries instead of entity objects
            status: Optional status to filter by
            
        Returns:
            List of matching forms as either entity objects or dictionaries
            
        Examples:
            >>> user_forms = form_dao.find_by_user(2)
            >>> submitted_forms = form_dao.find_by_user(2, status="submitted")
            >>> form_dicts = form_dao.find_by_user(2, as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name} WHERE creator_id = ?"
        params = [user_id]
        
        # Add status filter if provided
        if status is not None:
            status_str = status if isinstance(status, str) else str(status)
            query += " AND status = ?"
            params.append(status_str)
            
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
        
    def find_by_type(self, form_type: str, 
                    as_dict: bool = False,
                    status: Optional[Union[FormStatus, str]] = None) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Find forms of a specific type, optionally filtered by status.
        
        Args:
            form_type: Type of form (e.g., 'ICS-213')
            as_dict: When True, return dictionaries instead of entity objects
            status: Optional status to filter by
            
        Returns:
            List of matching forms as either entity objects or dictionaries
            
        Examples:
            >>> ics213_forms = form_dao.find_by_type('ICS-213')
            >>> finalized_ics213 = form_dao.find_by_type('ICS-213', status=FormStatus.FINALIZED)
            >>> form_dicts = form_dao.find_by_type('ICS-214', as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name} WHERE form_type = ?"
        params = [form_type]
        
        # Add status filter if provided
        if status is not None:
            status_str = status if isinstance(status, str) else str(status)
            query += " AND status = ?"
            params.append(status_str)
            
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
        
    def search(self, search_term: str, incident_id: Optional[int] = None, 
              form_type: Optional[str] = None) -> List[Form]:
        """
        Search for forms by title or content, with optional filtering.
        
        Args:
            search_term: Term to search for in title and content
            incident_id: Optional incident ID to filter by
            form_type: Optional form type to filter by
            
        Returns:
            List of matching forms
            
        Examples:
            >>> results = form_dao.search("evacuation")
            >>> incident_results = form_dao.search("supplies", incident_id=3)
            >>> ics213_results = form_dao.search("urgent", form_type='ICS-213')
        """
        # Build base query with title search
        query = f"""
            SELECT DISTINCT f.* FROM {self.table_name} f
            LEFT JOIN form_versions v ON f.id = v.form_id
            WHERE (f.title LIKE ? OR v.content LIKE ?)
        """
        params = [f"%{search_term}%", f"%{search_term}%"]
        
        # Add incident filter if provided
        if incident_id is not None:
            query += " AND f.incident_id = ?"
            params.append(incident_id)
            
        # Add form type filter if provided
        if form_type is not None:
            query += " AND f.form_type = ?"
            params.append(form_type)
            
        cursor = self.db_manager.execute(query, params)
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def delete_cascade(self, form_id: int) -> bool:
        """
        Delete a form and all its versions and attachments.
        
        Args:
            form_id: ID of the form to delete
            
        Returns:
            True if the form was deleted, False otherwise
            
        Example:
            >>> success = form_dao.delete_cascade(5)
            >>> if success:
            >>>     print("Form and all related data deleted successfully")
        """
        with self.db_manager.transaction() as tx:
            # Delete attachments first (to satisfy foreign key constraints)
            tx.execute("DELETE FROM attachments WHERE form_id = ?", (form_id,))
            
            # Delete versions
            tx.execute("DELETE FROM form_versions WHERE form_id = ?", (form_id,))
            
            # Finally delete the form
            cursor = tx.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (form_id,))
            
            # Invalidate cache manually since we're not using BaseDAO's delete method
            self._invalidate_cache()
            
            return cursor.rowcount > 0
            
    def set_form_status(self, form_id: int, status: Union[FormStatus, str]) -> bool:
        """
        Update a form's status.
        
        Args:
            form_id: ID of the form to update
            status: New status
            
        Returns:
            True if the form was updated, False otherwise
            
        Examples:
            >>> form_dao.set_form_status(5, FormStatus.FINALIZED)
            >>> form_dao.set_form_status(6, "submitted")
        """
        status_str = status if isinstance(status, str) else str(status)
        now = datetime.now()
        
        # Use the standardized update method
        update_data = {
            'status': status_str,
            'updated_at': now
        }
        
        # This will also handle cache invalidation
        return self.update(form_id, update_data)
        
    def find_recent(self, as_dict: bool = False, limit: int = 10, 
                   incident_id: Optional[int] = None) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Find recently updated forms.
        
        Args:
            as_dict: When True, return dictionaries instead of entity objects
            limit: Maximum number of forms to return
            incident_id: Optional incident ID to filter by
            
        Returns:
            List of recent forms as either entity objects or dictionaries
            
        Examples:
            >>> recent_forms = form_dao.find_recent(limit=5)
            >>> incident_forms = form_dao.find_recent(incident_id=3)
            >>> form_dicts = form_dao.find_recent(as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name}"
        params = []
        
        if incident_id is not None:
            query += " WHERE incident_id = ?"
            params.append(incident_id)
            
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
