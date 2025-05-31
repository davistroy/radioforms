"""Multi-form database service for enhanced form management.

This module provides comprehensive database operations for managing multiple
form types in the RadioForms application. It extends the basic database
functionality to support advanced features like search indexing, bulk operations,
form metadata management, and version history tracking.

Key Features:
    - Multi-form type storage and retrieval
    - Full-text search capabilities across form content
    - Batch operations for performance
    - Form metadata extraction and indexing
    - Version history tracking and management
    - Advanced querying with filters and sorting
    - Search optimization for 100+ forms
    - Concurrent access safety

Classes:
    MultiFormService: Main service for multi-form database operations
    FormSearchIndex: Text search indexing and querying
    FormMetadataExtractor: Extract searchable metadata from forms
    BatchOperationResult: Result object for batch operations

Functions:
    create_multi_form_service: Factory function for service creation
    extract_searchable_text: Utility for extracting searchable content

Notes:
    This implementation follows the CLAUDE.md principles for database operations
    with emphasis on performance, reliability, and maintainability.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager

# Import database and form system
try:
    from ..database.connection import DatabaseManager, DatabaseError
    from ..models.base_form import BaseForm, FormType, FormStatus
    from ..forms.ics213 import ICS213Form
    from ..models.ics214 import ICS214Form
except ImportError:
    # For standalone testing
    import sys
    sys.path.append('.')
    from src.database.connection import DatabaseManager, DatabaseError
    from src.models.base_form import BaseForm, FormType, FormStatus
    from src.forms.ics213 import ICS213Form
    from src.models.ics214 import ICS214Form


logger = logging.getLogger(__name__)


class FormSortField(Enum):
    """Available sort fields for form queries."""
    
    CREATED_DATE = "created_at"
    UPDATED_DATE = "updated_at"
    FORM_TYPE = "form_type"
    INCIDENT_NAME = "incident_name"
    TITLE = "title"
    STATUS = "status"
    CREATED_BY = "created_by"


class SortDirection(Enum):
    """Sort direction options."""
    
    ASCENDING = "ASC"
    DESCENDING = "DESC"


@dataclass
class FormQuery:
    """Query parameters for form searches.
    
    Encapsulates all possible query parameters for searching and filtering
    forms in the database with advanced options for sorting and pagination.
    
    Attributes:
        form_types: Filter by specific form types (None = all types).
        incident_names: Filter by specific incident names (None = all incidents).
        statuses: Filter by specific statuses (None = all statuses).
        created_by: Filter by form creator (None = all creators).
        search_text: Full-text search across form content (None = no search).
        created_after: Filter forms created after this date (None = no limit).
        created_before: Filter forms created before this date (None = no limit).
        sort_field: Field to sort results by.
        sort_direction: Direction to sort results.
        limit: Maximum number of results to return (None = no limit).
        offset: Number of results to skip for pagination (default 0).
        
    Example:
        >>> query = FormQuery(
        ...     form_types=[FormType.ICS_213],
        ...     search_text="urgent",
        ...     sort_field=FormSortField.CREATED_DATE,
        ...     sort_direction=SortDirection.DESCENDING,
        ...     limit=50
        ... )
    """
    
    form_types: Optional[List[FormType]] = None
    incident_names: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    created_by: Optional[str] = None
    search_text: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_field: FormSortField = FormSortField.UPDATED_DATE
    sort_direction: SortDirection = SortDirection.DESCENDING
    limit: Optional[int] = None
    offset: int = 0


@dataclass
class BatchOperationResult:
    """Result of a batch database operation.
    
    Provides comprehensive information about the success or failure
    of batch operations on multiple forms.
    
    Attributes:
        success_count: Number of operations that succeeded.
        failure_count: Number of operations that failed.
        total_count: Total number of operations attempted.
        errors: List of error messages for failed operations.
        successful_ids: List of form IDs that were processed successfully.
        failed_ids: List of form IDs that failed to process.
        execution_time: Time taken to execute the batch operation.
        
    Example:
        >>> result = BatchOperationResult()
        >>> result.add_success(123)
        >>> result.add_failure(456, "Database constraint violation")
        >>> print(f"Success rate: {result.success_rate:.1%}")
    """
    
    success_count: int = 0
    failure_count: int = 0
    total_count: int = 0
    errors: List[str] = field(default_factory=list)
    successful_ids: List[int] = field(default_factory=list)
    failed_ids: List[int] = field(default_factory=list)
    execution_time: float = 0.0
    
    def add_success(self, form_id: int) -> None:
        """Record a successful operation."""
        self.success_count += 1
        self.total_count += 1
        self.successful_ids.append(form_id)
    
    def add_failure(self, form_id: int, error: str) -> None:
        """Record a failed operation."""
        self.failure_count += 1
        self.total_count += 1
        self.failed_ids.append(form_id)
        self.errors.append(f"Form {form_id}: {error}")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as a decimal (0.0 to 1.0)."""
        return self.success_count / self.total_count if self.total_count > 0 else 0.0
    
    @property
    def is_complete_success(self) -> bool:
        """Check if all operations succeeded."""
        return self.failure_count == 0 and self.success_count > 0
    
    @property
    def has_failures(self) -> bool:
        """Check if any operations failed."""
        return self.failure_count > 0


class FormSearchIndex:
    """Full-text search index for form content.
    
    Provides efficient full-text search capabilities across form content
    using SQLite's FTS (Full-Text Search) capabilities. Maintains a
    separate search index that is updated whenever forms are modified.
    
    The search index extracts and indexes searchable text from:
    - Form titles and subjects
    - Message content and descriptions
    - Person names and positions
    - Incident names and locations
    - Tags and keywords
    
    Example:
        >>> search_index = FormSearchIndex(db_manager)
        >>> search_index.initialize()
        >>> results = search_index.search("urgent medical")
        >>> form_ids = [result[0] for result in results]
    """
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize search index.
        
        Args:
            db_manager: Database manager for connection handling.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(f"{__name__}.FormSearchIndex")
    
    def initialize(self) -> None:
        """Initialize the search index tables and triggers.
        
        Creates the FTS virtual table and triggers to keep it synchronized
        with the main forms table.
        
        Raises:
            DatabaseError: If initialization fails.
        """
        self.logger.info("Initializing form search index...")
        
        try:
            with self.db_manager.get_transaction() as conn:
                # Create FTS virtual table for search
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS forms_fts USING fts5(
                        form_id UNINDEXED,
                        content
                    )
                """)
                
                # Create trigger to update FTS when forms are inserted
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS forms_fts_insert 
                    AFTER INSERT ON forms
                    BEGIN
                        INSERT INTO forms_fts(form_id, content) 
                        VALUES (NEW.id, NEW.form_type || ' ' || 
                                COALESCE(NEW.title, '') || ' ' || 
                                COALESCE(NEW.incident_name, '') || ' ' ||
                                COALESCE(NEW.data, ''));
                    END
                """)
                
                # Create trigger to update FTS when forms are updated
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS forms_fts_update 
                    AFTER UPDATE ON forms
                    BEGIN
                        DELETE FROM forms_fts WHERE form_id = OLD.id;
                        INSERT INTO forms_fts(form_id, content) 
                        VALUES (NEW.id, NEW.form_type || ' ' || 
                                COALESCE(NEW.title, '') || ' ' || 
                                COALESCE(NEW.incident_name, '') || ' ' ||
                                COALESCE(NEW.data, ''));
                    END
                """)
                
                # Create trigger to remove from FTS when forms are deleted
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS forms_fts_delete 
                    AFTER DELETE ON forms
                    BEGIN
                        DELETE FROM forms_fts WHERE form_id = OLD.id;
                    END
                """)
            
            self.logger.info("Form search index initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize search index: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def rebuild_index(self) -> int:
        """Rebuild the entire search index from scratch.
        
        This method clears the existing search index and rebuilds it
        from all forms in the database. Use this if the index becomes
        corrupted or after bulk data operations.
        
        Returns:
            int: Number of forms indexed.
            
        Raises:
            DatabaseError: If rebuild fails.
        """
        self.logger.info("Rebuilding form search index...")
        
        try:
            with self.db_manager.get_transaction() as conn:
                # Clear existing index
                conn.execute("DELETE FROM forms_fts WHERE 1=1")
                
                # Rebuild from all forms
                conn.execute("""
                    INSERT INTO forms_fts(form_id, content)
                    SELECT id, form_type || ' ' || 
                           COALESCE(title, '') || ' ' || 
                           COALESCE(incident_name, '') || ' ' ||
                           COALESCE(data, '')
                    FROM forms
                """)
                
                # Get count of indexed forms
                cursor = conn.execute("SELECT COUNT(*) FROM forms_fts")
                count = cursor.fetchone()[0]
            
            self.logger.info(f"Rebuilt search index with {count} forms")
            return count
            
        except Exception as e:
            error_msg = f"Failed to rebuild search index: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def search(self, query: str, limit: Optional[int] = None) -> List[Tuple[int, float]]:
        """Search for forms matching the query text.
        
        Args:
            query: Search query text.
            limit: Maximum number of results to return.
            
        Returns:
            List of tuples containing (form_id, relevance_score).
            
        Raises:
            DatabaseError: If search fails.
        """
        if not query or not query.strip():
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                # Use FTS MATCH query with ranking
                sql = """
                    SELECT form_id, rank
                    FROM forms_fts 
                    WHERE forms_fts MATCH ?
                    ORDER BY rank
                """
                
                params = [query.strip()]
                
                if limit:
                    sql += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(sql, params)
                results = cursor.fetchall()
                
                # Convert rank to relevance score (higher is better)
                return [(row[0], -row[1]) for row in results]
                
        except Exception as e:
            self.logger.error(f"Search failed for query '{query}': {e}")
            raise DatabaseError(f"Search failed: {e}") from e


class MultiFormService:
    """Service for managing multiple form types in the database.
    
    This service provides high-level database operations for managing
    multiple form types with advanced features like search, filtering,
    bulk operations, and version history.
    
    Key capabilities:
    - Store and retrieve any form type (ICS-213, ICS-214, etc.)
    - Full-text search across form content
    - Advanced filtering and sorting
    - Bulk operations for performance
    - Version history tracking
    - Form metadata management
    - Concurrent access safety
    
    Example:
        >>> service = MultiFormService(db_manager)
        >>> service.initialize()
        >>> 
        >>> # Save a form
        >>> form_id = service.save_form(my_form, "John Doe")
        >>> 
        >>> # Search forms
        >>> query = FormQuery(search_text="urgent", limit=10)
        >>> results = service.search_forms(query)
        >>> 
        >>> # Load forms
        >>> forms = service.load_forms([form_id])
    """
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize multi-form service.
        
        Args:
            db_manager: Database manager for connection handling.
        """
        self.db_manager = db_manager
        self.search_index = FormSearchIndex(db_manager)
        self.logger = logging.getLogger(f"{__name__}.MultiFormService")
    
    def initialize(self) -> None:
        """Initialize the multi-form service.
        
        Sets up search indexing and any other required initialization.
        
        Raises:
            DatabaseError: If initialization fails.
        """
        self.logger.info("Initializing multi-form service...")
        
        try:
            # Initialize search index
            self.search_index.initialize()
            
            self.logger.info("Multi-form service initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize multi-form service: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def save_form(self, form: BaseForm, created_by: str = "Unknown") -> int:
        """Save a form to the database.
        
        Args:
            form: Form instance to save.
            created_by: User who is saving the form.
            
        Returns:
            int: Database ID of the saved form.
            
        Raises:
            DatabaseError: If save operation fails.
        """
        try:
            # Extract form metadata
            form_type = form.get_form_type().value
            
            # Extract searchable fields from form data
            title = self._extract_form_title(form)
            incident_name = self._extract_incident_name(form)
            status = form.get_status().value if hasattr(form, 'get_status') else 'draft'
            
            # Serialize just the form data properly
            if hasattr(form, 'data'):
                # For forms with a data attribute, serialize the data
                json_data = json.dumps(form.data.to_dict())
            else:
                # Fallback to full form dict
                json_data = json.dumps(form.to_dict())
            
            with self.db_manager.get_transaction() as conn:
                cursor = conn.execute("""
                    INSERT INTO forms (
                        form_type, incident_name, title, data, 
                        created_by, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (form_type, incident_name, title, json_data, created_by, status))
                
                form_id = cursor.lastrowid
                
                # Create initial version record
                conn.execute("""
                    INSERT INTO form_versions (
                        form_id, version, data, changed_by, change_description
                    ) VALUES (?, 1, ?, ?, 'Initial creation')
                """, (form_id, json_data, created_by))
            
            self.logger.debug(f"Saved form {form_type} with ID {form_id}")
            return form_id
            
        except Exception as e:
            error_msg = f"Failed to save form: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def update_form(self, form_id: int, form: BaseForm, changed_by: str = "Unknown", 
                   change_description: str = "Updated") -> bool:
        """Update an existing form in the database.
        
        Args:
            form_id: Database ID of the form to update.
            form: Updated form instance.
            changed_by: User making the change.
            change_description: Description of what was changed.
            
        Returns:
            bool: True if update was successful.
            
        Raises:
            DatabaseError: If update operation fails.
        """
        try:
            # Extract form metadata
            form_type = form.get_form_type().value
            
            # Extract searchable fields
            title = self._extract_form_title(form)
            incident_name = self._extract_incident_name(form)
            status = form.get_status().value if hasattr(form, 'get_status') else 'draft'
            
            # Serialize just the form data properly
            if hasattr(form, 'data'):
                # For forms with a data attribute, serialize the data
                json_data = json.dumps(form.data.to_dict())
            else:
                # Fallback to full form dict
                json_data = json.dumps(form.to_dict())
            
            with self.db_manager.get_transaction() as conn:
                # Get current version
                cursor = conn.execute(
                    "SELECT version FROM forms WHERE id = ?", (form_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise DatabaseError(f"Form with ID {form_id} not found")
                
                current_version = result[0]
                new_version = current_version + 1
                
                # Update main form record
                conn.execute("""
                    UPDATE forms SET 
                        form_type = ?, incident_name = ?, title = ?, 
                        data = ?, status = ?, version = ?
                    WHERE id = ?
                """, (form_type, incident_name, title, json_data, status, new_version, form_id))
                
                # Create version record
                conn.execute("""
                    INSERT INTO form_versions (
                        form_id, version, data, changed_by, change_description
                    ) VALUES (?, ?, ?, ?, ?)
                """, (form_id, new_version, json_data, changed_by, change_description))
            
            self.logger.debug(f"Updated form ID {form_id} to version {new_version}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to update form {form_id}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def load_form(self, form_id: int) -> Optional[BaseForm]:
        """Load a form from the database by ID.
        
        Args:
            form_id: Database ID of the form to load.
            
        Returns:
            BaseForm: Loaded form instance or None if not found.
            
        Raises:
            DatabaseError: If load operation fails.
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT form_type, data FROM forms WHERE id = ?
                """, (form_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                form_type_str, json_data = result
                
                # Create appropriate form instance
                form = self._create_form_from_type(form_type_str)
                if form:
                    # Parse the stored data and load it into the form
                    data_dict = json.loads(json_data)
                    if hasattr(form, 'data'):
                        form.data = form.data.__class__.from_dict(data_dict)
                    else:
                        form.from_dict(data_dict)
                
                return form
                
        except Exception as e:
            error_msg = f"Failed to load form {form_id}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def load_forms(self, form_ids: List[int]) -> List[BaseForm]:
        """Load multiple forms by their IDs.
        
        Args:
            form_ids: List of database IDs to load.
            
        Returns:
            List[BaseForm]: List of loaded forms (may be shorter if some IDs not found).
            
        Raises:
            DatabaseError: If load operation fails.
        """
        if not form_ids:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                # Create placeholders for IN clause
                placeholders = ','.join('?' * len(form_ids))
                
                cursor = conn.execute(f"""
                    SELECT id, form_type, data 
                    FROM forms 
                    WHERE id IN ({placeholders})
                    ORDER BY updated_at DESC
                """, form_ids)
                
                forms = []
                for row in cursor.fetchall():
                    db_id, form_type_str, json_data = row
                    
                    try:
                        form = self._create_form_from_type(form_type_str)
                        
                        if form:
                            # Parse the stored data and load it into the form
                            data_dict = json.loads(json_data)
                            if hasattr(form, 'data'):
                                form.data = form.data.__class__.from_dict(data_dict)
                            else:
                                form.from_dict(data_dict)
                            forms.append(form)
                    
                    except Exception as e:
                        self.logger.warning(f"Failed to load form {db_id}: {e}")
                        continue
                
                return forms
                
        except Exception as e:
            error_msg = f"Failed to load forms {form_ids}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def search_forms(self, query: FormQuery) -> List[Dict[str, Any]]:
        """Search for forms matching the query criteria.
        
        Args:
            query: Query parameters for search and filtering.
            
        Returns:
            List of dictionaries containing form metadata and IDs.
            
        Raises:
            DatabaseError: If search operation fails.
        """
        try:
            with self.db_manager.get_connection() as conn:
                # Build base query
                sql = """
                    SELECT id, form_type, form_number, incident_name, title, 
                           created_by, created_at, updated_at, status, version
                    FROM forms
                    WHERE 1=1
                """
                params = []
                
                # Add filters
                if query.form_types:
                    type_placeholders = ','.join('?' * len(query.form_types))
                    sql += f" AND form_type IN ({type_placeholders})"
                    params.extend([ft.value for ft in query.form_types])
                
                if query.incident_names:
                    incident_placeholders = ','.join('?' * len(query.incident_names))
                    sql += f" AND incident_name IN ({incident_placeholders})"
                    params.extend(query.incident_names)
                
                if query.statuses:
                    status_placeholders = ','.join('?' * len(query.statuses))
                    sql += f" AND status IN ({status_placeholders})"
                    params.extend(query.statuses)
                
                if query.created_by:
                    sql += " AND created_by = ?"
                    params.append(query.created_by)
                
                if query.created_after:
                    sql += " AND created_at >= ?"
                    params.append(query.created_after.isoformat())
                
                if query.created_before:
                    sql += " AND created_at <= ?"
                    params.append(query.created_before.isoformat())
                
                # Handle text search
                if query.search_text:
                    # Get matching form IDs from search index
                    matching_ids = self.search_index.search(query.search_text)
                    
                    if matching_ids:
                        id_placeholders = ','.join('?' * len(matching_ids))
                        sql += f" AND id IN ({id_placeholders})"
                        params.extend([match[0] for match in matching_ids])
                    else:
                        # No matches found, return empty result
                        return []
                
                # Add sorting
                sql += f" ORDER BY {query.sort_field.value} {query.sort_direction.value}"
                
                # Add pagination
                if query.limit:
                    sql += " LIMIT ?"
                    params.append(query.limit)
                
                if query.offset > 0:
                    sql += " OFFSET ?"
                    params.append(query.offset)
                
                cursor = conn.execute(sql, params)
                
                # Convert results to dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'form_type': row[1],
                        'form_number': row[2],
                        'incident_name': row[3],
                        'title': row[4],
                        'created_by': row[5],
                        'created_at': row[6],
                        'updated_at': row[7],
                        'status': row[8],
                        'version': row[9]
                    })
                
                return results
                
        except Exception as e:
            error_msg = f"Failed to search forms: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def delete_form(self, form_id: int) -> bool:
        """Delete a form from the database.
        
        Args:
            form_id: Database ID of the form to delete.
            
        Returns:
            bool: True if deletion was successful.
            
        Raises:
            DatabaseError: If delete operation fails.
        """
        try:
            with self.db_manager.get_transaction() as conn:
                cursor = conn.execute("DELETE FROM forms WHERE id = ?", (form_id,))
                
                if cursor.rowcount == 0:
                    return False
                
                self.logger.debug(f"Deleted form ID {form_id}")
                return True
                
        except Exception as e:
            error_msg = f"Failed to delete form {form_id}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def bulk_delete_forms(self, form_ids: List[int]) -> BatchOperationResult:
        """Delete multiple forms in a batch operation.
        
        Args:
            form_ids: List of form IDs to delete.
            
        Returns:
            BatchOperationResult: Result of the batch operation.
        """
        start_time = datetime.now()
        result = BatchOperationResult()
        
        try:
            with self.db_manager.get_transaction() as conn:
                for form_id in form_ids:
                    try:
                        cursor = conn.execute("DELETE FROM forms WHERE id = ?", (form_id,))
                        
                        if cursor.rowcount > 0:
                            result.add_success(form_id)
                        else:
                            result.add_failure(form_id, "Form not found")
                    
                    except Exception as e:
                        result.add_failure(form_id, str(e))
            
            result.execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Bulk delete completed: {result.success_count}/{result.total_count} successful")
            
        except Exception as e:
            result.execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Bulk delete failed: {e}")
            # Mark remaining forms as failed
            for form_id in form_ids[result.total_count:]:
                result.add_failure(form_id, f"Transaction failed: {e}")
        
        return result
    
    def get_form_versions(self, form_id: int) -> List[Dict[str, Any]]:
        """Get version history for a form.
        
        Args:
            form_id: Database ID of the form.
            
        Returns:
            List of version records.
            
        Raises:
            DatabaseError: If operation fails.
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT version, changed_by, change_description, created_at
                    FROM form_versions 
                    WHERE form_id = ?
                    ORDER BY version DESC
                """, (form_id,))
                
                versions = []
                for row in cursor.fetchall():
                    versions.append({
                        'version': row[0],
                        'changed_by': row[1],
                        'change_description': row[2],
                        'created_at': row[3]
                    })
                
                return versions
                
        except Exception as e:
            error_msg = f"Failed to get versions for form {form_id}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary containing various statistics.
            
        Raises:
            DatabaseError: If operation fails.
        """
        try:
            with self.db_manager.get_connection() as conn:
                stats = {}
                
                # Total form count
                cursor = conn.execute("SELECT COUNT(*) FROM forms")
                stats['total_forms'] = cursor.fetchone()[0]
                
                # Forms by type
                cursor = conn.execute("""
                    SELECT form_type, COUNT(*) 
                    FROM forms 
                    GROUP BY form_type
                """)
                stats['forms_by_type'] = dict(cursor.fetchall())
                
                # Forms by status
                cursor = conn.execute("""
                    SELECT status, COUNT(*) 
                    FROM forms 
                    GROUP BY status
                """)
                stats['forms_by_status'] = dict(cursor.fetchall())
                
                # Recent activity (last 7 days)
                cursor = conn.execute("""
                    SELECT COUNT(*) 
                    FROM forms 
                    WHERE created_at >= datetime('now', '-7 days')
                """)
                stats['recent_forms'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            error_msg = f"Failed to get statistics: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def _extract_form_title(self, form: BaseForm) -> str:
        """Extract a searchable title from a form."""
        try:
            if hasattr(form, 'data'):
                data = form.data
                
                # ICS-213 forms use subject as title
                if hasattr(data, 'subject') and data.subject:
                    return data.subject[:200]  # Limit length
                
                # ICS-214 forms may use incident_name or a constructed title
                if hasattr(data, 'incident_name') and data.incident_name:
                    name_part = getattr(data, 'name', '') 
                    if name_part:
                        return f"{data.incident_name} - {name_part}"[:200]
                    return data.incident_name[:200]
            
            return f"Untitled {form.get_form_type().value}"
            
        except Exception:
            return f"Untitled {form.get_form_type().value}"
    
    def _extract_incident_name(self, form: BaseForm) -> str:
        """Extract incident name from a form."""
        try:
            if hasattr(form, 'data') and hasattr(form.data, 'incident_name'):
                return form.data.incident_name[:100]  # Limit length
            return ""
        except Exception:
            return ""
    
    def _create_form_from_type(self, form_type_str: str) -> Optional[BaseForm]:
        """Create a form instance from type string."""
        try:
            if form_type_str == 'ICS-213':
                return ICS213Form()
            elif form_type_str == 'ICS-214':
                return ICS214Form()
            else:
                self.logger.warning(f"Unknown form type: {form_type_str}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create form of type {form_type_str}: {e}")
            return None


# Factory function

def create_multi_form_service(db_manager: DatabaseManager) -> MultiFormService:
    """Factory function for creating multi-form service instances.
    
    Args:
        db_manager: Database manager for connection handling.
        
    Returns:
        MultiFormService: Configured service instance.
    """
    service = MultiFormService(db_manager)
    service.initialize()
    return service


# Utility functions

def extract_searchable_text(form: BaseForm) -> str:
    """Extract searchable text content from a form.
    
    Args:
        form: Form to extract text from.
        
    Returns:
        str: Combined searchable text content.
    """
    searchable_parts = []
    
    try:
        # Add form type
        searchable_parts.append(form.get_form_type().value)
        
        # Extract data from form
        if hasattr(form, 'data'):
            data = form.data
            
            # Common fields
            for field_name in ['incident_name', 'subject', 'message', 'title', 'name']:
                if hasattr(data, field_name):
                    value = getattr(data, field_name)
                    if value and isinstance(value, str):
                        searchable_parts.append(value)
            
            # Person fields (names and positions)
            for person_field in ['to', 'from_person', 'prepared_by']:
                if hasattr(data, person_field):
                    person = getattr(data, person_field)
                    if hasattr(person, 'name') and person.name:
                        searchable_parts.append(person.name)
                    if hasattr(person, 'position') and person.position:
                        searchable_parts.append(person.position)
        
        # Add tags if available
        if hasattr(form, 'get_tags'):
            tags = form.get_tags()
            if tags:
                searchable_parts.extend(tags)
        
        return ' '.join(searchable_parts)
        
    except Exception as e:
        logger.warning(f"Failed to extract searchable text from form: {e}")
        return form.get_form_type().value  # Fallback to just form type