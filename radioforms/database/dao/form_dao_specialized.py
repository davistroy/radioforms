#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Form DAO with specialized query methods.

This extends the FormDAO with optimized query methods for common operations
across the application.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, overload

from radioforms.database.dao.form_dao import FormDAO
from radioforms.database.models.form import Form, FormStatus
from radioforms.database.models.form_version import FormVersion
from radioforms.database.db_manager import DatabaseManager


class EnhancedFormDAO(FormDAO):
    """
    Enhanced Data Access Object for Form operations with specialized query methods.
    
    This class extends the base FormDAO with additional query methods that optimize
    common access patterns and provide more targeted data retrieval options.
    """
    
    def find_forms_with_content_by_type(self, form_type: str, 
                                      status: Optional[Union[FormStatus, str]] = None,
                                      limit: int = 50,
                                      as_dict: bool = False) -> List[Tuple[Union[Form, Dict[str, Any]], Dict[str, Any]]]:
        """
        Find forms of a specific type with their content.
        
        This specialized query retrieves forms of the specified type along with their
        content in a single efficient query, avoiding multiple database lookups.
        
        Args:
            form_type: The type of form to retrieve (e.g., "ICS-213")
            status: Optional status to filter by
            limit: Maximum number of forms to return
            as_dict: When True, return form as dictionary instead of entity
            
        Returns:
            List of tuples containing (form, content) where form is either a Form object
            or dictionary based on the as_dict parameter
            
        Example:
            >>> # Get all ICS-213 message forms with their content
            >>> forms_with_content = form_dao.find_forms_with_content_by_type("ICS-213")
            >>> for form, content in forms_with_content:
            >>>     print(f"Form: {form.title}, Message: {content.get('message')}")
        """
        # First get the forms of the specified type
        query = f"""
        SELECT f.*, v.content, v.version_number 
        FROM {self.table_name} f
        INNER JOIN (
            SELECT form_id, MAX(version_number) as latest_version
            FROM form_versions
            GROUP BY form_id
        ) latest ON f.id = latest.form_id
        INNER JOIN form_versions v ON f.id = v.form_id AND v.version_number = latest.latest_version
        WHERE f.form_type = ?
        """
        
        params = [form_type]
        
        # Add status filter if provided
        if status is not None:
            status_str = status if isinstance(status, str) else str(status)
            query += " AND f.status = ?"
            params.append(status_str)
            
        # Add limit
        query += " ORDER BY f.updated_at DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        # Process results
        result = []
        for row in rows:
            row_dict = dict(row)
            content_str = row_dict.pop('content', None)
            
            # Parse content
            try:
                import json
                content = json.loads(content_str) if content_str else {}
            except json.JSONDecodeError:
                content = {}
                
            # Create form object or dictionary
            if as_dict:
                form_dict = {k: v for k, v in row_dict.items() if k != 'version_number'}
                result.append((form_dict, content))
            else:
                form = self._row_to_entity(row_dict)
                result.append((form, content))
                
        return result
    
    def find_forms_by_status(self, status: Union[FormStatus, str], 
                           incident_id: Optional[int] = None,
                           form_type: Optional[str] = None,
                           limit: int = 50,
                           as_dict: bool = False) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Find forms with a specific status, with optional incident and type filters.
        
        This method provides an efficient way to retrieve forms based on their status,
        with additional optional filters for incident and form type.
        
        Args:
            status: Status to filter by (FormStatus enum or string)
            incident_id: Optional incident ID to filter by
            form_type: Optional form type to filter by
            limit: Maximum number of forms to return
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of forms matching the criteria
            
        Example:
            >>> # Get finalized ICS-213 forms for a specific incident
            >>> finalized = form_dao.find_forms_by_status(
            ...     FormStatus.FINALIZED, 
            ...     incident_id=5, 
            ...     form_type="ICS-213"
            ... )
        """
        status_str = status if isinstance(status, str) else str(status)
        
        query = f"SELECT * FROM {self.table_name} WHERE status = ?"
        params = [status_str]
        
        # Add incident filter if provided
        if incident_id is not None:
            query += " AND incident_id = ?"
            params.append(incident_id)
            
        # Add form type filter if provided
        if form_type is not None:
            query += " AND form_type = ?"
            params.append(form_type)
            
        # Add limit and order
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def advanced_search(self, 
                       title: Optional[str] = None,
                       form_type: Optional[str] = None,
                       incident_id: Optional[int] = None,
                       creator_id: Optional[int] = None,
                       status: Optional[Union[FormStatus, str]] = None,
                       content_search: Optional[str] = None,
                       date_from: Optional[datetime] = None,
                       date_to: Optional[datetime] = None,
                       order_by: str = "updated_at DESC",
                       limit: int = 50,
                       as_dict: bool = False) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Advanced search for forms with multiple optional filter criteria.
        
        This method provides a flexible way to search for forms based on
        various criteria, allowing for complex filtering with a single query.
        Content search is performed against the latest version of each form.
        
        Args:
            title: Optional title pattern to search for
            form_type: Optional form type to filter by
            incident_id: Optional incident ID to filter by
            creator_id: Optional creator ID to filter by
            status: Optional status to filter by
            content_search: Optional text to search for in form content
            date_from: Optional start of date range filter (based on created_at)
            date_to: Optional end of date range filter (based on created_at)
            order_by: SQL ORDER BY clause for sorting results
            limit: Maximum number of results to return
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of matching forms
            
        Example:
            >>> # Search for resource request forms with "urgent" in the content
            >>> urgent_requests = form_dao.advanced_search(
            ...     form_type="ICS-213",
            ...     content_search="urgent"
            ... )
        """
        # Base query parts
        base_query = f"SELECT DISTINCT f.* FROM {self.table_name} f"
        where_parts = []
        params = []
        
        # Add content search if provided (requires join with form_versions)
        if content_search:
            base_query += """
            INNER JOIN (
                SELECT form_id, MAX(version_number) as latest_version
                FROM form_versions
                GROUP BY form_id
            ) latest ON f.id = latest.form_id
            INNER JOIN form_versions v ON f.id = v.form_id AND v.version_number = latest.latest_version
            """
            where_parts.append("v.content LIKE ?")
            params.append(f"%{content_search}%")
        
        # Add title search
        if title:
            where_parts.append("f.title LIKE ?")
            params.append(f"%{title}%")
            
        # Add form type filter
        if form_type:
            where_parts.append("f.form_type = ?")
            params.append(form_type)
            
        # Add incident filter
        if incident_id is not None:
            where_parts.append("f.incident_id = ?")
            params.append(incident_id)
            
        # Add creator filter
        if creator_id is not None:
            where_parts.append("f.creator_id = ?")
            params.append(creator_id)
            
        # Add status filter
        if status is not None:
            status_str = status if isinstance(status, str) else str(status)
            where_parts.append("f.status = ?")
            params.append(status_str)
            
        # Add date range filters
        if date_from:
            where_parts.append("f.created_at >= ?")
            params.append(date_from)
            
        if date_to:
            where_parts.append("f.created_at <= ?")
            params.append(date_to)
            
        # Combine where parts if any
        if where_parts:
            query = f"{base_query} WHERE {' AND '.join(where_parts)}"
        else:
            query = base_query
            
        # Add order by and limit
        query += f" ORDER BY f.{order_by} LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_forms_with_attachments(self, 
                                  incident_id: Optional[int] = None, 
                                  limit: int = 50,
                                  as_dict: bool = False) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Find forms that have file attachments.
        
        This specialized query retrieves forms that have at least one attachment,
        useful for finding forms with supporting documentation.
        
        Args:
            incident_id: Optional incident ID to filter by
            limit: Maximum number of forms to return
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of forms that have at least one attachment
            
        Example:
            >>> # Get forms with attachments for incident #5
            >>> forms = form_dao.find_forms_with_attachments(incident_id=5)
        """
        query = f"""
        SELECT DISTINCT f.* FROM {self.table_name} f
        INNER JOIN attachments a ON f.id = a.form_id
        """
        
        params = []
        
        # Add incident filter if provided
        if incident_id is not None:
            query += " WHERE f.incident_id = ?"
            params.append(incident_id)
            
        # Add limit and order
        query += " ORDER BY f.updated_at DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_recently_modified_by_user(self, 
                                     user_id: int, 
                                     days: int = 7,
                                     as_dict: bool = False) -> Union[List[Form], List[Dict[str, Any]]]:
        """
        Find forms recently modified by a specific user.
        
        This specialized query finds forms that have been created or updated by the 
        specified user within the given time period.
        
        Args:
            user_id: ID of the user
            days: Number of days to look back for activity
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of forms recently modified by the user
            
        Example:
            >>> # Get forms modified by user #3 in the last 3 days
            >>> recent_forms = form_dao.find_recently_modified_by_user(3, days=3)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Query to find forms created by the user or with versions created by the user
        query = f"""
        SELECT DISTINCT f.* FROM {self.table_name} f
        LEFT JOIN form_versions v ON f.id = v.form_id
        WHERE (f.creator_id = ? AND f.created_at >= ?)
           OR (v.created_by = ? AND v.created_at >= ?)
        ORDER BY 
            CASE
                WHEN f.updated_at > f.created_at THEN f.updated_at
                ELSE f.created_at
            END DESC
        """
        
        params = [user_id, cutoff_date, user_id, cutoff_date]
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def get_form_count_by_type(self, incident_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get a count of forms by type.
        
        This method provides statistics on the number of forms of each type,
        optionally filtered by incident.
        
        Args:
            incident_id: Optional incident ID to filter by
            
        Returns:
            Dictionary mapping form types to counts
            
        Example:
            >>> counts = form_dao.get_form_count_by_type(incident_id=5)
            >>> print(f"ICS-213 forms: {counts.get('ICS-213', 0)}")
            >>> print(f"ICS-214 forms: {counts.get('ICS-214', 0)}")
        """
        query = f"""
        SELECT form_type, COUNT(*) as count
        FROM {self.table_name}
        """
        
        params = []
        
        # Add incident filter if provided
        if incident_id is not None:
            query += " WHERE incident_id = ?"
            params.append(incident_id)
            
        query += " GROUP BY form_type"
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        
        # Convert results to dictionary
        result = {}
        for row in cursor.fetchall():
            result[row['form_type']] = row['count']
            
        return result
